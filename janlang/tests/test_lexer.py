import os.path
import json
import lexer
import utils


def lex_file_json(path: str):
    with open(os.path.join("tests", "programs", path)) as f:
        tokens = list(lexer.RuleLexer(f.read()))
    return json.loads(utils.to_json(tokens))


def test_hello_world():
    assert lex_file_json("hello.jn") == [
        {"type": "Name", "fields": {"value": "print"}},
        {"type": "OpenParen"},
        {"type": "String", "fields": {"val": "hello world"}},
        {"type": "CloseParen"},
        {"type": "NL"},
        {"type": "EOF"},
    ]


def test_order_of_operations():
    print(lex_file_json("order_of_operations.jn"))
    assert lex_file_json("order_of_operations.jn") == [
        {"type": "VariableDeclaration"},
        {"type": "Name", "fields": {"value": "result"}},
        {"type": "Assign"},
        {"type": "Int", "fields": {"val": "1"}},
        {"type": "Plus"},
        {"type": "Int", "fields": {"val": "2"}},
        {"type": "Star"},
        {"type": "Int", "fields": {"val": "3"}},
        {"type": "NL"},
        {"type": "EOF"},
    ]
