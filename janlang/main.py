import argparse
from lark import Lark
from lark.indenter import Indenter
import interpreter
import lark_parser
import astree_constructor
import ast_json
import lexer
import _parser as parser

def main():
    arg_parser = argparse.ArgumentParser(description='Process some integers.')
    arg_parser.add_argument('main', type=str,
                        help='an integer for the accumulator')
    args = arg_parser.parse_args()
    text = ''
    with open(args.main) as f:
        text = f.read()
        print (args.main)
    tokens = []
    for i, token in enumerate(lexer.RuleLexer(text)):
        tokens.append(token)
        print(i, token)
    print(tokens)
    tree = parser.Parser(tokens).parse_module()
    print(ast_json.dumps(tree))
    interpreter.Interpreter().execute(tree)

if __name__ == '__main__':
    main()