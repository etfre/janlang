import astree as ast
from contextlib import contextmanager
import tokens
from typing import List, Type, Never, Generic, TypeVar

TokenType = TypeVar("TokenType", bound=tokens.BaseToken)

comparison_tokens: dict[Type[tokens.BaseToken], Type[ast.ComparisonOperator]] = {
    tokens.Eq: ast.Eq,
    tokens.NotEq: ast.NotEq,
    tokens.Gt: ast.Gt,
    tokens.GtE: ast.GtE,
    tokens.Lt: ast.Lt,
    tokens.LtE: ast.LtE,
}
binary_tokens_to_ast_nodes: dict[Type[tokens.BaseToken], Type[ast.Operator]] = {
    **comparison_tokens,
    tokens.Star: ast.Multiply,
    tokens.Plus: ast.Add,
    tokens.Minus: ast.Subtract,
}

class Parser:
    def __init__(self, _tokens):
        self.tokens: list[tokens.BaseToken] = _tokens
        self.pos = 0
        self.errors = []
        self._hard_fail_on_error = False
        self.statement_parse_order = (
            self.parse_function_definition,
            self.parse_class_definition,
            self.parse_return_statement,
            self.parse_if_statement,
            self.parse_while_statement,
            self.parse_for_statement,
            self.parse_continue_statement,
            self.parse_break_statement,
            self.parse_assert_statement,
            # self.parse_assign_and_declaration_statement,
            self.parse_declaration_statement,
            self.parse_assign_statement,
            self.parse_pass_statement,
            self.parse_simple_statement,  # last
        )
        self.primaries = (
            self.parse_name,
            self.parse_boolean,
            self.parse_string,
            self.parse_int,
            self.parse_null,
            self.parse_float,
            self.parse_list,
            self.parse_dictionary,
            self.parse_grouping,
        )


    def parse_root(self):
        main = self.parse_module()
        program = ast.Program(main)
        return program

    def parse_module(self):
        tok_length = len(self.tokens)
        body = self.parse_statements()
        tok = self.peek()
        if not isinstance(tok, tokens.EOF):
            self.hard_error("Did not parse all tokens in module")
        filtered_pass_body = [x for x in body if not isinstance(x, PassResult)]
        root_module = ast.Module(filtered_pass_body)
        return root_module

    def parse_statements(self):
        stmts: list[ast.BaseNode] = []
        while True:
            self.expect_greedy(tokens.NL, min_to_pass=0)
            if isinstance(self.peek(), (tokens.EOF, tokens.Dedent)):
                break

            result = self.parse_statement()
            if result is None:
                break
            stmts.append(result)
        return stmts

    def parse_statement(self) -> ast.BaseNode:
        """
        expecting a valid statement here, so hard error if everything errors
        """
        start_pos = self.pos
        for parse_fn in self.statement_parse_order:
            try:
                return parse_fn()
            except ParseError:
                self.pos = start_pos
        start_pos = self.pos
        self.hard_error()

    @contextmanager
    def advance_on_error(advance_to):
        yield

    @contextmanager
    def reraise_parse_error(self, msg=""):
        try:
            yield
        except ParseError as e:
            self.hard_error(msg)
        finally:
            pass

    def parse_function_definition(self):
        self.expect(tokens.FunctionDef)
        name = self.require(tokens.Name).value
        self.require(tokens.OpenParen)
        params = self.parse_parameters()
        self.require(tokens.CloseParen)
        body = self.colon_newline_and_block()
        return ast.FunctionDefinition(name, params, [], body)

    def parse_name_and_maybe_declaration(self):
        decl = self.match(tokens.VariableDeclaration)
        if not decl:
            return self.parse_name()
        mut = self.match(tokens.Mutable)
        is_mutable = bool(mut)
        name = self.parse_name()
        return ast.VariableDeclaration(name, is_mutable)

    def parse_declaration_statement(self):
        decl = self.match(tokens.VariableDeclaration)
        if not decl:
            self.error()
        mut = self.match(tokens.Mutable)
        is_mutable = bool(mut)
        name = self.parse_name()
        if not name:
            self.hard_error()
        # if also assigning to a variable decrement pos by one for parse_assign_statement
        if isinstance(self.peek(), tokens.Assign):
            self.pos -= 1
            assert self.pos >= 0
        return ast.VariableDeclaration(name, is_mutable)

    def parse_assign_statement(self):
        left = self.parse_primary()
        if not self.match(tokens.Assign):
            self.error()
        if not isinstance(left, (ast.Name, ast.Index)):
            self.hard_error()
        right = self.parse_expression()
        return ast.Assignment(left, right)

    def parse_if_statement(self):
        self.expect(tokens.If)
        test = self.parse_expression()
        body = self.colon_newline_and_block()
        else_ifs = []
        else_body = None
        while else_body is None:
            try:
                self.expect(tokens.Else)
            except ParseError:
                break
            next_tok = self.peek()
            if isinstance(next_tok, tokens.If):
                self.advance()
                elif_test = self.parse_expression()
                elif_body = self.colon_newline_and_block()
                else_ifs.append((elif_test, elif_body))
            else:
                else_body = self.colon_newline_and_block()
                
        return ast.IfStatement(test, body, else_ifs, else_body)
    
    def colon_newline_and_block(self):
        self.require(tokens.Colon)
        self.require(tokens.NL)
        return self.parse_block()

    def parse_while_statement(self):
        self.expect(tokens.While)
        test = self.parse_expression()
        body = self.colon_newline_and_block()
        return ast.WhileStatement(test, body)

    def parse_for_statement(self):
        self.expect(tokens.For)
        name = self.parse_name_and_maybe_declaration()
        self.require(tokens.In)
        iter = self.parse_expression()
        body = self.colon_newline_and_block()
        return ast.ForStatement(name, iter, body)

    def parse_continue_statement(self):
        self.expect(tokens.Continue)
        self.require(tokens.NL)
        return ast.ContinueStatement()

    def parse_break_statement(self):
        self.expect(tokens.Break)
        self.require(tokens.NL)
        return ast.BreakStatement()

    def parse_return_statement(self):
        self.expect(tokens.Return)
        try:
            val = self.parse_expression()
        except ParseError:
            val = None
        self.require(tokens.NL)
        return ast.Return(val)

    def parse_block(self):
        self.expect(tokens.Indent)
        stmts = self.parse_statements()
        if not stmts:
            self.hard_error()
        self.require(tokens.Dedent)
        filtered_pass_stmts = [x for x in stmts if not isinstance(x, PassResult)]
        return ast.Block(filtered_pass_stmts)

    def parse_operations(self, next_parse_fn, operator_tokens):
        operands: list[ast.Expr] = []
        operators: list[ast.Operator] = []
        while True:
            try:
                if len(operands) == len(operators):
                    node = next_parse_fn()
                    add_list = operands
                else:
                    tok = self.expect(*operator_tokens)
                    node: ast.Operator = binary_tokens_to_ast_nodes[type(tok)]()
                    add_list = operators
            except ParseError as e:
                if not operands:
                    raise e
                break
            else:
                add_list.append(node)
        assert not operands or len(operands) - 1 == len(operators)
        return operands, operators

    def binop_tree(self, next_parse_fn, operator_tokens):
        operands, operators = self.parse_operations(next_parse_fn, operator_tokens)
        left = operands[0]
        for i, op in enumerate(operators, start=1):
            right = operands[i]
            left = ast.BinOp(left, op, right)
        return left

    def parse_pass_statement(self):
        self.expect(tokens.Pass)
        self.require(tokens.NL)
        return PassResult()

    def parse_simple_statement(self):
        result = self.parse_expression()
        self.require(tokens.NL)
        return result

    def parse_expression(self) -> ast.Expr:
        return self.parse_compare()

    def parse_compare(self):
        op_tokens = tuple(comparison_tokens)
        (left, *comparators), operators = self.parse_operations(
            self.parse_additive, op_tokens
        )
        if not comparators:
            return left
        return ast.Compare(left, operators, comparators)

    def parse_additive(self):
        op_tokens = (tokens.Plus, tokens.Minus)
        return self.binop_tree(self.parse_multiplicative, op_tokens)

    def parse_multiplicative(self):
        op_tokens = (tokens.Star, tokens.Slash)
        return self.binop_tree(self.parse_unary, op_tokens)

    def parse_grouping(self):
        self.expect(tokens.OpenParen)
        with self.reraise_parse_error("Expecting a valid expression"):
            expr = self.parse_expression()
        self.require(tokens.CloseParen)
        return expr

    def parse_unary(self):
        try:
            tok = self.expect(tokens.Not, tokens.Minus)
        except ParseError:
            return self.parse_primary()
        expr = self.parse_unary()
        if isinstance(tok, tokens.Not):
            return ast.Not(expr)
        if isinstance(tok, tokens.Minus):
            return ast.Negative(expr)
        raise NotImplementedError

    def parse_primary(self):
        start_pos = self.pos
        node: ast.Expr | None = None
        for fn in self.primaries:
            try:
                node = fn()
            except ParseError:
                self.pos = start_pos
            else:
                break
        if not node:
            self.error()
        chain_functions = (self.finish_call, self.finish_attribute, self.finish_index)
        while True:
            next_node = self.make_chain(node, chain_functions)
            if not next_node:
                break
            node = next_node
        return node

    def make_chain(self, root: ast.Expr, chain_functions) -> ast.Expr | None:
        next_node: ast.Expr | None = None
        start_pos = self.pos
        for fn in chain_functions:
            try:
                next_node = fn(root)
            except ParseError:
                pass
            else:
                break
        if next_node is None:
            self.pos = start_pos
        return next_node

    def finish_index(self, val: ast.Expr):
        self.expect(tokens.OpenBracket)
        expr = self.parse_expression()
        self.expect(tokens.CloseBracket)
        return ast.Index(val, expr)

    def finish_attribute(self, val: ast.Expr):
        self.expect(tokens.Period)
        name = self.expect(tokens.Name)
        return ast.Attribute(val, name.value)

    def finish_call(self, func: ast.Expr):
        self.expect(tokens.OpenParen)
        args = self.parse_listvals()
        self.expect(tokens.CloseParen)
        return ast.Call(func, args, {})

    # def finish_list(self, func):
    #     self.expect(tokens.OpenParen)
    #     args = self.parse_listvals()
    #     self.expect(tokens.CloseParen)
    #     return ast.List(func, args, {})

    def parse_name(self):
        tok = self.expect(tokens.Name)
        return ast.Name(tok.value)

    def parse_assert_statement(self):
        self.expect(tokens.Assert)
        with self.reraise_parse_error("Expecting a valid expression for assert"):
            test = self.parse_expression()
        return ast.AssertStatement(test)

    def parse_boolean(self):
        tok = self.expect(tokens.TrueToken, tokens.FalseToken)
        if isinstance(tok, tokens.TrueToken):
            return ast.TrueNode()
        else:
            return ast.FalseNode()
        
    def parse_null(self):
        tok = self.expect(tokens.NullToken)
        return ast.Null()

    def parse_float(self):
        tok = self.expect(tokens.Float)
        return ast.Float(tok.val)

    def parse_int(self):
        tok = self.expect(tokens.Int)
        return ast.Integer(tok.val)

    def parse_list(self):
        self.expect(tokens.OpenBracket)
        list_vals = self.parse_listvals()
        self.require(tokens.CloseBracket, error='Expecting ]')
        return ast.List(list_vals)

    def parse_dictionary(self):
        self.expect(tokens.OpenBrace)
        vals = self.parse_dictionary_vals()
        self.require(tokens.CloseBrace, error='Expecting }')
        d = ast.Dictionary(vals)
        return d

    def parse_string(self):
        tok = self.expect(tokens.String)
        return ast.String(tok.val)

    def parse_parameters(self):
        start = self.pos
        vals: list[ast.Parameter] = []
        pos = self.pos
        while True:
            try:
                param_name = self.parse_name().value
                vals.append(ast.Parameter(param_name))
                pos = self.pos
                self.expect(tokens.Comma)
                pos = self.pos
            except ParseError:
                break
        self.pos = pos
        return vals

    def parse_dictionary_vals(self):
        # (expr ':' expr (',' expr ':' expr)*)*
        start = self.pos
        vals = []
        # pos = self.pos
        # while True:
        #     try:
        #         key = self.parse_expression()
        #         self.require(tokens.Colon)
        #         try:
        #             val = self.parse_expression()
        #         except ParseError:
        #             self.hard_error()
        #     except ParseError:
        #         break
        #     pos = self.pos
        #     self.expect(tokens.Comma)
        #     pos = self.pos
        # self.pos = pos
        return vals

    def parse_listvals(self):
        # (expr (',' expr)*)*
        start = self.pos
        vals: list[ast.Expr] = []
        pos = self.pos
        while True:
            try:
                vals.append(self.parse_expression())
                pos = self.pos
                self.expect(tokens.Comma)
                pos = self.pos
            except ParseError:
                break
        self.pos = pos
        return vals
    
    def parse_class_definition(self):
        self.expect(tokens.ClassDef)
        name = self.require(tokens.Name)
        self.require(tokens.Colon)
        self.require(tokens.NL)
        self.require(tokens.Indent)
        has_pass = False
        class_body_stmts: list[ast.FunctionDefinition] = []
        while True:
            self.expect_greedy(tokens.NL, min_to_pass=0)
            tok = self.peek()
            if isinstance(tok, (tokens.EOF, tokens.Dedent)):
                break
            elif isinstance(tok, tokens.Pass):
                has_pass = True
                self.advance()
                continue
            try:
                result = self.parse_method()
            except ParseError:
                break
            class_body_stmts.append(result)
        if not (class_body_stmts or has_pass):
            self.hard_error()
        self.require(tokens.Dedent)        
        cls_def = ast.ClassDefinition(name.value, class_body_stmts)
        return cls_def
    
    def parse_method(self):
        name = self.require(tokens.Name).value
        self.require(tokens.OpenParen)
        params = self.parse_parameters()
        self.require(tokens.CloseParen)
        body = self.colon_newline_and_block()
        return ast.FunctionDefinition(name, params, [], body)

    def expect_greedy(self, *types, min_to_pass=1):
        count = 0
        while self.match(*types):
            count += 1
        if count < min_to_pass:
            self.error()

    def expect(self, *types):
        next_tok = self.peek()
        for tok_type in types:
            if isinstance(next_tok, tok_type):
                return self.advance()
        self.error()

    def require(self, token_type, error=''):
        try:
            return self.expect(token_type)
        except ParseError as e:
            self.hard_error(error)

    def match(self, *types):
        try:
            return self.expect(*types)
        except ParseError:
            pass

    def advance(self):
        curr = self.tokens[self.pos]
        self.pos += 1
        return curr


    def peek(self):
        try:
            return self.tokens[self.pos]
        except IndexError:
            return
        
    def peek_many(self, count: int):
        toks: list[tokens.BaseToken] = []
        for i in range(count):
            try:
                toks.append(self.tokens[self.pos + i])
            except IndexError:
                return
        return toks

    def _error(self, msg, error_class) -> Never:
        tok = self.peek()
        text, line = tok.source
        error_msg = f'Got an error at line {line}, "{text}" {tok}'
        if msg:
            error_msg += f"\n{msg}"
        raise error_class(error_msg)

    def error(self, msg=""):
        self._error(msg, ParseError)

    def hard_error(self, msg="") -> Never:
        self._error(msg, HardParseError)


class PassResult():
    pass

class ParseError(Exception):
    pass


class HardParseError(Exception):
    pass
