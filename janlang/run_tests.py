import os
import fnmatch
import os.path
import argparse
import interpreter
import ast_json
import lexer
import errors
import _parser as parser
import ast_json
import traceback

def main():
    arg_parser = argparse.ArgumentParser(description='Process some integers.')
    arg_parser.add_argument("-i", type=str)
    args = arg_parser.parse_args()
    print(args.i)
    passed = []
    parse_errors = []
    failed = []
    for root, _, file_names in os.walk('../tests'):
        for file_name in sorted(file_names):
            path = os.path.join(root, file_name)
            if args.i and not fnmatch.fnmatch(path, args.i):
                continue
            try:
                tokenizer = lexer.RuleLexer.from_path(path)
                tokens = list(tokenizer.tokenize())
                program = parser.Parser(tokens).parse_root()
                # print(ast_json.dumps(program))
                interpreter.Interpreter().execute(program)
            except Exception as e:
                failed.append((path, e))
            else:
                passed.append(path)
    for path, e in failed:
        print(f'Exception in {path}')
        print("".join(traceback.format_exception(e)))
    print(f'{len(passed)} tests passed, {len(failed)} tests had errors')

if __name__ == '__main__':
    main()