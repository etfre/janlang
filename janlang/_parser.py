import astree as ast
import tokens

class Parser:

    def __init__(self, _tokens):
        self.tokens = _tokens
        self.pos = 0
        self.statement_parse_order = (
            self.parse_if_statement,
            self.parse_simple_statement,
        )
        self.atom_starts = (
            self.parse_name,
            self.parse_int,
            self.parse_float,
        )
        self.atoms = (
            self.parse_call,
            self.parse_name,
            self.parse_int,
            self.parse_float,
        )
        self.comparison_tokens = {
            tokens.Eq: ast.Eq, 
            tokens.NotEq: ast.NotEq, 
            tokens.Gt: ast.Gt, 
            tokens.GtE: ast.GtE, 
            tokens.Lt: ast.Lt, 
            tokens.LtE: ast.LtE, 
        }
        self.binary_tokens_to_ast_nodes = {
            **self.comparison_tokens,
            tokens.Star: ast.Multiply,
            tokens.Plus: ast.Add,
            tokens.Minus: ast.Subtract,
        }

    def parse_module(self):
        tok_length = len(self.tokens)
        body = self.parse_statements()
        root_module = ast.Module(body)
        return root_module

    def parse_statements(self):
        stmts = []
        next_tok = self.peek() 
        while True:
            self.expect_greedy(tokens.NL, min_to_pass=0)
            try:
                stmt = self.parse_statement()
            except ParseError as e:
                break
            else:
                stmts.append(stmt)
        return stmts


    def parse_statement(self):
        self.expect_greedy(tokens.NL, min_to_pass=0)
        if self.match(tokens.EOF):
            self.error()
        start_pos = self.pos
        for parse_fn in self.statement_parse_order:
            try:
                return parse_fn()
            except ParseError:
                self.pos = start_pos
        self.error()


    def parse_if_statement(self):
        next_tok = self.expect(tokens.If)
    
    def parse_operations(self, next_parse_fn, operator_tokens):
        operands = []
        operators = []
        while True:
            try:
                if len(operands) == len(operators):
                    node = next_parse_fn()
                    add_list = operands
                else:
                    tok = self.expect(operator_tokens)
                    node = self.binary_tokens_to_ast_nodes[type(tok)]()
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

    def parse_simple_statement(self):
        result = self.parse_expression()
        self.expect((tokens.NL, tokens.EOF))
        return result
        
    def parse_expression(self):
        return self.parse_compare()

    def parse_compare(self):
        op_tokens = tuple(self.comparison_tokens)
        nodes, operators = self.parse_operations(self.parse_additive, op_tokens)
        if len(nodes) == 1:
            return nodes[0]

    def parse_additive(self):
        op_tokens = (tokens.Plus, tokens.Minus)
        return self.binop_tree(self.parse_multiplicative, op_tokens)

    def parse_multiplicative(self):
        op_tokens = (tokens.Star, tokens.Slash)
        return self.binop_tree(self.parse_atom, op_tokens)

    def parse_atom(self):
        start_pos = self.pos
        for fn in self.atoms:
            try:
                return fn()
            except ParseError:
                pass
            self.pos = start_pos
        self.error()

    def parse_name(self):
        tok = self.expect(tokens.Name)
        return ast.Name(tok.val)

    def parse_call(self):
        print('abc', self.peek())
        func = self.parse_name()
        print('def')
        self.expect(tokens.OpenParen)
        self.expect(tokens.CloseParen)
        return ast.Call(func, [], {})

    def parse_float(self):
        tok = self.expect(tokens.Float)
        return ast.Float(tok.val)

    def parse_int(self):
        tok = self.expect(tokens.Int)
        return ast.Integer(tok.val)

    def parse_listvals(self):
        # (expr (',' expr)*)*
        start = self.pos
        vals = [] 
        expr = self.parse_expression()
        

    def expect_greedy(self, types, min_to_pass=1):
        count = 0
        while self.match(types):
            count += 1
        if count < min_to_pass:
            self.error()

    def expect(self, types):
        if not isinstance(types, (list, tuple)):
            types = [types]
        next_tok = self.peek()
        for tok_type in types:
            if isinstance(next_tok, tok_type):
                return self.advance()
        self.error()

    def match(self, types):
        try:
            return self.expect(types)
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

    def error(self, msg='Error'):
        raise ParseError(self.pos)

class ParseError(Exception):
    pass