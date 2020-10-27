import ast


class BaseToken:
    
    def __init__(self, *args, **kwargs):
        pass

class Name(BaseToken):
    
    def __init__(self, value):
        self.value = value

class OrToken(BaseToken):
    pass

class OpenParen(BaseToken):
    pass

class CloseParen(BaseToken):
    pass    

class OptionalGroupingOpeningToken(BaseToken):
    pass

class OptionalGroupingClosingToken(BaseToken):
    pass

class Whitespace(BaseToken):

    def __init__(self, text): 
        self.text = text

class NamedRuleToken(BaseToken):
    
    def __init__(self, name):
        self.name = name

class NL(BaseToken):
    pass

class Indent(BaseToken):
    pass

class Dedent(BaseToken):
    pass

class RepetitionToken(BaseToken):

    def __init__(self, low=0, high=None):
        self.low = low
        self.high = high
