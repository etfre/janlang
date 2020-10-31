from lark import Lark
from lark.indenter import Indenter
import interpreter
import lark_parser
import astree_constructor
import ast_json
import lexer
import _parser as parser

class TreeIndenter(Indenter):
    NL_type = '_NL'
    OPEN_PAREN_types = []
    CLOSE_PAREN_types = []
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 4

lark_parser = Lark(lark_parser.grammar, parser='lalr', start='module', postlex=TreeIndenter(), propagate_positions=True, maybe_placeholders=True)

test_tree = \
"""
2 + 3 * 4
foobar
"""

def test():
    tokens = []
    for token in lexer.RuleLexer(test_tree):
        tokens.append(token)
        print(token)
    tree = parser.Parser(tokens).parse_module()
    print(ast_json.dumps(tree))
    # lark_tree = lark_parser.parse(test_tree)
    # print(lark_tree.pretty())
    # root = astree_constructor.parse_node(lark_tree)
    interpreter.Interpreter().execute(tree)

if __name__ == '__main__':
    test()