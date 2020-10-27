from lark import Lark
from lark.indenter import Indenter
import interpreter
import lark_parser
import astree_constructor
import lexer

class TreeIndenter(Indenter):
    NL_type = '_NL'
    OPEN_PAREN_types = []
    CLOSE_PAREN_types = []
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 4

parser = Lark(lark_parser.grammar, parser='lalr', start='module', postlex=TreeIndenter(), propagate_positions=True, maybe_placeholders=True)

test_tree = \
"""
abcdef
    hij
lmn
def fib(a, b, c="def"):
    "c"
    
"""

def test():
    for token in lexer.RuleLexer(test_tree):
        print(token)
    lark_tree = parser.parse(test_tree)
    print(lark_tree.pretty())
    root = astree_constructor.parse_node(lark_tree)
    interpreter.Interpreter().execute(root)

if __name__ == '__main__':
    test()