from lark import Lark
from lark.indenter import Indenter
import interpreter
import lark_parser
import astree_constructor

class TreeIndenter(Indenter):
    NL_type = '_NL'
    OPEN_PAREN_types = []
    CLOSE_PAREN_types = []
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 4

parser = Lark(lark_parser.grammar, parser='lalr', start='module', postlex=TreeIndenter())

test_tree = \
"""
var a = "b"
var f = "eff"
if a:
    if f:
        a
if a:
    var b = "bee"
    b
    
"""

def test():
    lark_tree = parser.parse(test_tree)
    print(lark_tree.pretty())
    root = astree_constructor.parse_node(lark_tree)
    print(root)
    interpreter.Interpreter().execute(root)

if __name__ == '__main__':
    test()