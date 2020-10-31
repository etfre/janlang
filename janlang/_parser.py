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
            stmt = self.parse_statement()
            if stmt is None:
                break
            stmts.append(stmt)
        return stmts


    def parse_statement(self):
        self.expect_greedy(tokens.NL, min_to_pass=0)
        if self.match(tokens.EOF):
            return
        start_pos = self.pos
        for parse_fn in self.statement_parse_order:
            node = parse_fn()
            if node:
                return node
            self.pos = start_pos


    def parse_if_statement(self):
        next_tok = self.match(tokens.If)
        if not next_tok:
            return
    
    def parse_operations(self, next_parse_fn, operator_tokens):
        operands = []
        operators = []
        while True:
            if len(operands) == len(operators):
                node = next_parse_fn()
                add_list = operands
            else:
                tok = self.match(operator_tokens)
                node = None if tok is None else self.binary_tokens_to_ast_nodes[type(tok)]()
                add_list = operators
            if node is None:
                break
            add_list.append(node)
        assert not operands or len(operands) - 1 == len(operators)
        return operands, operators

    def binop_tree(self, next_parse_fn, operator_tokens):
        operands, operators = self.parse_operations(next_parse_fn, operator_tokens)
        if not operands:
            assert not operators
            return
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
        tok = self.peek()
        if isinstance(tok, tokens.Float):
            self.advance()
            return ast.Float(tok.val)
        if isinstance(tok, tokens.Int):
            self.advance()
            return ast.Integer(tok.val)

    def expect_greedy(self, types, min_to_pass=1):
        count = 0
        while self.match(types):
            count += 1
        if count < min_to_pass:
            self.error()

    def expect(self, types):
        result = self.match(types)
        if not result:
            self.error()
        return result

    def match(self, types):
        if not isinstance(types, (list, tuple)):
            types = [types]
        next_tok = self.peek()
        for tok_type in types:
            if isinstance(next_tok, tok_type):
                return self.advance()

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
        raise RuntimeError(self.pos)