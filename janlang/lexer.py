import re
from inspect import isclass
import tokens

class RuleLexer:

    def __init__(self, text):
        self.token_patterns = tuple((re.compile(p), _) for p, _ in (
            (r'\(', tokens.OpenParen),
            (r'\)', tokens.CloseParen),
            (r'\[', tokens.OpenBracket),
            (r'\]', tokens.CloseBracket),
            (r'\{', tokens.OpenBrace),
            (r'\}', tokens.CloseBrace),
            (r',', tokens.Comma),
            (r'==', tokens.Eq),
            (r'!=', tokens.NotEq),
            (r'>=', tokens.GtE),
            (r'<=', tokens.LtE),
            (r'>', tokens.Gt),
            (r'<', tokens.Lt),
            (r'=', tokens.Assign),
            (r'\*', tokens.Star),
            (r'\/', tokens.Slash),
            (r'-', tokens.Minus),
            (r'\+', tokens.Plus),
            (r'(\d*\.\d+|\d+\.\d*)', tokens.Float),
            (r'\d+', tokens.Int),
            (':', tokens.Colon),
            (r'\.', tokens.Period),
        ))
        self.keywords = {
            'assert': tokens.Assert,
            'break': tokens.Break,
            'class': tokens.ClassDef,
            'continue': tokens.Continue,
            'else': tokens.Else,
            'def': tokens.FunctionDef,
            'false': tokens.FalseToken,
            'for': tokens.For,
            'if': tokens.If,
            'in': tokens.In,
            'mut': tokens.Mutable,
            'not': tokens.Not,
            'null': tokens.NullToken,
            'pass': tokens.Pass,
            'return': tokens.Return,
            'this': tokens.This,
            'true': tokens.TrueToken,
            'var': tokens.VariableDeclaration,
            'while': tokens.While,
        }
        self.text = text
        self.pos = 0
        self.indentation_level = 0
        self.line = 1
        self.at_start_of_line = True

    def read_newline(self):
        self.advance()
        return tokens.NL()

    def read_whitespace(self):
        matched_text = ''
        while self.peek() == ' ':
            matched_text += ' '
            self.advance()
        return tokens.Whitespace(matched_text)

    def read_next_token(self):
        for pattern, token_creator in self.token_patterns:
            match = pattern.match(self.text, pos=self.pos) 
            if match:
                matched_text = self.text[self.pos:match.span()[-1]]
                token = token_creator(matched_text) if isclass(token_creator) else token_creator(matched_text)
                self.pos = match.span()[-1]
                return token
        raise RuntimeError(f'Cannot tokenize text: {self.text[self.pos:]}')

    def read_start_of_line(self):
        self.at_start_of_line = False
        spaces = 0
        start = self.pos
        curr = self.peek()
        while curr == ' ':
            spaces += 1
            curr = self.text[start + spaces]
        is_empty_line = curr == '\n'
        if is_empty_line:
            whitespace_to_yield = spaces
            level_change = 0
        else:
            indents, remainder = divmod(spaces, 4)
            assert not remainder
            level_change = indents - self.indentation_level
            whitespace_to_yield = spaces - abs(level_change)*4
        if whitespace_to_yield > 0:
            for _ in range(whitespace_to_yield):
                self.advance()
            yield tokens.Whitespace(' ' * whitespace_to_yield)
        if level_change == 1:
            self.pos += 4
            yield tokens.Indent()
        elif level_change > 1:
            raise RuntimeError('Indent cant be > 1')
        else:
            for i in range(0, level_change, -1):
                yield tokens.Dedent()
        self.indentation_level += level_change
        assert self.indentation_level >= 0

    @property
    def is_at_end(self):
        return self.pos >= len(self.text)

    def peek(self):
        try:
            return self.text[self.pos]
        except IndexError:
            return

    def match(self, val):
        if self.is_at_end:
            return False
        end = self.pos + len(val)
        is_match = self.text[self.pos:end] == val
        if is_match:
            self.pos += len(val)
        return is_match

    def advance(self):
        char = self.peek()
        self.pos += 1
        return char

    def read_keyword_or_name(self):
        start = self.pos
        name = self.advance()
        while not self.is_at_end:
            ch = self.peek()
            if not (ch.isalnum() or ch == '_'):
                break
            name += ch
            self.advance()
        if name in self.keywords:
            return self.keywords[name]()
        return tokens.Name(name)

    def parse_operator(self):
        for text, tok in self.operators:
            if self.match(text):
                return tok

    def read_string(self, delim):
        val = ''
        if not self.advance() == delim:
            self.error()
        ch = self.advance()
        while ch != delim:
            val += ch
            ch = self.advance()
            if ch is None:
                self.error()
        return tokens.String(val)

    def tokenize(self):
        pos = self.pos
        for tok in self._tokenize():
            source = (self.text[pos:self.pos], self.line)
            # print(tok, source)
            tok.source = source
            pos = self.pos
            if not isinstance(tok, tokens.Whitespace):
                yield tok

    def _tokenize(self):
        while not self.is_at_end:
            if self.at_start_of_line:
                yield from self.read_start_of_line()
            ch = self.peek()
            if ch in ('"', "'"):
                yield self.read_string(ch)
                continue
            if ch == '\n':
                yield self.read_newline()
                self.at_start_of_line = True
                self.line += 1
                continue
            if ch == ' ':
                yield self.read_whitespace() # yield so tokenize can keep track of position
                continue
            if ch.isalpha() or ch == '_':
                yield self.read_keyword_or_name()
                continue
            yield self.read_next_token()
        yield tokens.NL()
        for i in range(self.indentation_level):
            yield tokens.Dedent()
        yield tokens.EOF()
            # token, self.pos = self.read_next_token(self.pos)
            # yield token

    def error(self):
        raise RuntimeError('abc')

    @classmethod
    def from_path(cls, path: str):
        with open(path) as f:
            return cls(f.read())