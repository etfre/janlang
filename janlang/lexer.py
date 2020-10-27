import re
from inspect import isclass
import tokens

class RuleLexer:

    def __init__(self, text):
        self.token_patterns = tuple((re.compile(p, re.I), _) for p, _ in (
            (r'\n', self.read_newline),
            (r'[ ]+', self.read_whitespace),
            (r'[_a-zA-Z0-9]+', tokens.Name),
            (r'\|', tokens.OrToken),
            (r'\(', tokens.OpenParen),
            (r'\)', tokens.CloseParen),
            (r'\[', tokens.OptionalGroupingOpeningToken),
            (r'\]', tokens.OptionalGroupingClosingToken),
        ))

        self.text = text
        self.pos = 0
        self.indentation_level = 0
        self.at_start_of_line = True

    def read_newline(self, matched_text):
        self.at_start_of_line = True
        return tokens.NL()

    def read_whitespace(self, matched_text):
        return tokens.Whitespace(matched_text)

    def read_next_token(self, pos):
        for pattern, token_creator in self.token_patterns:
            match = pattern.match(self.text, pos=pos) 
            if match:
                matched_text = self.text[pos:match.span()[-1]]
                token = token_creator(matched_text) if isclass(token_creator) else token_creator(matched_text)
                if hasattr(token, 'consumed_char_count'):
                    pos += token.consumed_char_count + 1
                else:
                    pos = match.span()[-1]
                return token, pos
        raise RuntimeError(f'Cannot tokenize text: {self.text[pos:]}')

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
        end = self.pos + len(val)
        return self.text[self.pos:end] == val

    def advance(self):
        char = self.peek()
        self.pos += 1
        return char

    def 

    def __iter__(self):
        while not self.is_at_end:
            if self.at_start_of_line:
                yield from self.read_start_of_line()
            
            tok = self.read_key
            token, self.pos = self.read_next_token(self.pos)
            yield token
