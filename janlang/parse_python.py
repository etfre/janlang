import ast
import astpretty
import sys

print(sys.argv)
with open(sys.argv[1]) as f:
    src = f.read()
    src_ast = ast.parse(src)
    print(src)
    astpretty.pprint(src_ast.body[0], show_offsets=False)