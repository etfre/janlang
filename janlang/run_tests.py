import os
import os.path
import argparse
import interpreter
import ast_json
import lexer
import _parser as parser

def main():
    arg_parser = argparse.ArgumentParser(description='Process some integers.')
    args = arg_parser.parse_args()
    for root, _, file_names in os.walk('../tests'):
        for file_name in file_names:
            path = os.path.join(root, file_name)
            print(f'Running {path}')
            tokenizer = lexer.RuleLexer.from_path(path)
            tokens = list(tokenizer.tokenize())
            program = parser.Parser(tokens).parse_root()
            interpreter.Interpreter().execute(program)
            print(path)

if __name__ == '__main__':
    main()