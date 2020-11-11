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
        ))
        self.keywords = {
            'if': tokens.If,
            'while': tokens.While,
            'for': tokens.For,
            'in': tokens.In,
            'continue': tokens.Continue,
            'break': tokens.Break,
            'return': tokens.Return,
            'fun': tokens.FunctionDef,
            'var': tokens.VariableDeclaration,
            'mut': tokens.Mutable,
        }
        self.text = text
        self.pos = 0
        self.indentation_level = 0
        self.at_start_of_line = True

    def read_newline(self):
        self.at_start_of_line = True
        self.advance()
        return tokens.NL()

    def read_whitespace(self, matched_text):
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
        spaces = 0
        while self.text[self.pos] == ' ':
            spaces += 1
            self.pos += 1
        indents, remainder = divmod(spaces, 4)
        level_change = indents - self.indentation_level
        if level_change == 1:
            yield tokens.Indent()
        elif level_change > 1:
            raise RuntimeError('Indent cant be >1')
        else:
            for i in range(0, level_change, -1):
                yield tokens.Dedent()
        self.indentation_level += level_change
        assert self.indentation_level >= 0
        self.at_start_of_line = False

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


    def __iter__(self):
        while not self.is_at_end:
            if self.at_start_of_line:
                yield from self.read_start_of_line()
            ch = self.peek()
            if ch in ('"', "'"):
                yield self.read_string(ch)
                continue
            if ch == '\n':
                yield self.read_newline()
                continue
            if ch == ' ':
                self.advance()
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