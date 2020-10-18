import ast
import sys

print(sys.argv)
with open(sys.argv[1]) as f:
    src = f.read()
    src_ast = ast.parse(src)
    print(src)
    print(ast.dump(src_ast.body[0]))