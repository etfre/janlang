from lark import Lark
from lark.indenter import Indenter
import lark_parser
import astree_constructor

class TreeIndenter(Indenter):
    NL_type = '_NL'
    OPEN_PAREN_types = []
    CLOSE_PAREN_types = []
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 8

parser = Lark(lark_parser.grammar, parser='lalr', postlex=TreeIndenter())

test_tree = """
a
    b
    c
        d
        e
    f
        g
"""

def test():
    lark_tree = parser.parse(test_tree).pretty()
    print(lark_tree)

if __name__ == '__main__':
    test()