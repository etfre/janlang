import argparse
import interpreter
import ast_json
import lexer
import _parser as parser

def main():
    arg_parser = argparse.ArgumentParser(description='Process some integers.')
    arg_parser.add_argument('main', type=str,
                        help='an integer for the accumulator')
    args = arg_parser.parse_args()
    tokenizer = lexer.RuleLexer.from_path(args.main)
    tokens = list(tokenizer.tokenize())
    tree = parser.Parser(tokens).parse_root()
    print(ast_json.dumps(tree))
    interpreter.Interpreter().execute(tree)

if __name__ == '__main__':
    main()