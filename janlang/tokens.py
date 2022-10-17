import ast


class BaseToken:
    
    def __init__(self, *args, **kwargs):
        self.source = None
        pass

class Assert(BaseToken):
    pass

class TrueToken(BaseToken):
    pass

class FalseToken(BaseToken):
    pass

class NullToken(BaseToken):
    pass

class OrToken(BaseToken):
    pass

class OpenParen(BaseToken):
    pass

class CloseParen(BaseToken):
    pass

class Gt(BaseToken):
    pass
class GtE(BaseToken):
    pass
class Lt(BaseToken):
    pass
class LtE(BaseToken):
    pass
class Eq(BaseToken):
    pass

class Not(BaseToken):
    pass

class NotEq(BaseToken):
    pass

class Assign(BaseToken):
    pass

class Colon(BaseToken):
    pass

class Minus(BaseToken):
    pass

class Plus(BaseToken):
    pass

class Star(BaseToken):
    pass

class Slash(BaseToken):
    pass

class Dot(BaseToken):
    pass

class OpenBrace(BaseToken):
    pass

class CloseBrace(BaseToken):
    pass

class OpenBracket(BaseToken):
    pass

class CloseBracket(BaseToken):
    pass

class Comma(BaseToken):
    pass

class Return(BaseToken):
    pass

class Whitespace(BaseToken):

    def __init__(self, text): 
        self.text = text

class NamedRuleToken(BaseToken):
    
    def __init__(self, name):
        self.name = name

class Int(BaseToken):
    
    def __init__(self, val):
        self.val = val

class Float(BaseToken):
    
    def __init__(self, val):
        self.val = val

class NL(BaseToken):
    pass

class Indent(BaseToken):
    pass

class Dedent(BaseToken):
    pass
class Name(BaseToken):
    def __init__(self, value):
        super().__init__()
        self.value = value
    def __repr__(self) -> str:
        return f'{self.value} - {super().__repr__()}'


class If(BaseToken):
    pass

class While(BaseToken):
    pass

class For(BaseToken):
    pass

class Continue(BaseToken):
    pass

class Break(BaseToken):
    pass

class In(BaseToken):
    pass

class FunctionDef(BaseToken):
    pass

class VariableDeclaration(BaseToken):
    pass

class Mutable(BaseToken):
    pass

class Period(BaseToken):
    pass

class EOF(BaseToken):
    pass

class String(BaseToken):
    def __init__(self, val):
        super().__init__()
        self.val = val