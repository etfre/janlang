from __future__ import annotations
from values.base import BaseValue
from typing import List as ListType, TypeAlias


class BaseNode:
    pass


class Expr(BaseNode):
    pass


class Program(BaseNode):
    def __init__(self, main):
        self.main = main


class Block(BaseNode):
    def __init__(self, statements):
        self.statements: ListType[BaseNode] = statements


class Module(BaseNode):
    def __init__(self, body):
        self.body = body


class ArgumentReference(BaseNode):
    def __init__(self, value: str):
        self.value = value


class Whitespace(BaseNode):
    def __init__(self, value: str):
        self.value = value


class Gt:
    def evaluate(self, left, right):
        return left > right


class GtE:
    def evaluate(self, left, right):
        return left >= right


class Lt:
    def evaluate(self, left, right):
        return left < right


class LtE:
    def evaluate(self, left, right):
        return left <= right


class Eq:
    def evaluate(self, left, right):
        return left == right


class NotEq:
    def evaluate(self, left, right):
        return left != right


ComparisonOperator: TypeAlias = Gt | GtE | Lt | LtE | Eq | NotEq


class Add:
    def evaluate(self, left, right):
        return left + right


class Subtract:
    def evaluate(self, left, right):
        return left - right


class Multiply:
    def evaluate(self, left, right):
        return left * right


class Divide:
    def evaluate(self, left, right):
        return left / right


Operator: TypeAlias = Add | Subtract | Multiply | Divide | ComparisonOperator


class String(Expr):
    def __init__(self, value: str):
        self.value: str = value


class Integer(Expr):
    def __init__(self, value: int):
        self.value: int = int(value)


class IfStatement(BaseNode):
    def __init__(self, test, orelse, body):
        self.test: Expr = test
        self.orelse: Expr = orelse
        self.body: Block = body


class Float(Expr):
    def __init__(self, value: float):
        self.value = float(value)


class Not(BaseNode):
    def __init__(self, expr):
        self.expr: BaseValue = expr


class Negative(Expr):
    def __init__(self, value) -> None:
        self.value: Expr = value


class UnaryOp(Expr):
    def __init__(self, operation, operand):
        self.operation = operation
        self.operand = operand


class BinOp(Expr):
    def __init__(self, left, op, right):
        self.left: Expr = left
        self.op: ComparisonOperator = op
        self.right: Expr = right


class Exponent(Expr):
    def __init__(self, left: Expr, right: Expr):
        self.left = left
        self.right = right

class Or(Expr):
    def __init__(self, left: Expr, right: Expr):
        self.left = left
        self.right = right

class And(Expr):
    def __init__(self, left: Expr, right: Expr):
        self.left = left
        self.right = right


class Compare(Expr):
    def __init__(self, left, ops, comparators):
        self.left: ListType[BaseNode] = left
        self.ops: ListType[ComparisonOperator] = ops
        self.comparators: ListType[BaseNode] = comparators


class List(Expr):
    def __init__(self, items):
        self.items: ListType[BaseNode] = items


class Dictionary(Expr):
    def __init__(self, kv_pairs):
        self.kv_pairs = kv_pairs


class Attribute(Expr):
    def __init__(self, attribute_of: Expr, name: Expr):
        self.attribute_of = attribute_of
        self.name = name

    def typecheck(self):
        pass


class Index(Expr):
    def __init__(self, index_of: Expr, index: Expr):
        self.index_of = index_of
        self.index = index


class Slice(Expr):
    def __init__(self, slice_of, start, stop, step):
        self.slice_of: Expr = slice_of
        self.start = start
        self.stop = stop
        self.step = step


class Parameter(Expr):
    def __init__(self, name):
        self.name = name


class Call(Expr):
    def __init__(self, fn: Expr, args: list[Expr], kwargs):
        self.fn = fn
        self.args = args
        self.kwargs = kwargs


class Assignment(BaseNode):
    def __init__(self, left: BaseNode, right: Expr):
        self.left: BaseNode = left
        self.right = right


class WhileStatement(BaseNode):
    def __init__(self, test, body):
        self.test: Expr = test
        self.body: Block = body


class ForStatement(BaseNode):
    def __init__(self, left, iter, body):
        self.left: Name | VariableDeclaration = left
        self.iter: Expr = iter
        self.body: Block = body


class ContinueStatement(BaseNode):
    pass

class BreakStatement(BaseNode):
    pass


class Name(Expr):
    def __init__(self, value):
        self.value: str = value


class FunctionDefinition(BaseNode):
    def __init__(self, name: str, parameters: list[Parameter], defaults, body: Block):
        self.name = name
        self.parameters = parameters
        self.defaults = defaults
        self.body = body


class ClassDefinition(BaseNode):
    def __init__(self, name: str, parameters, defaults, body):
        self.name = name
        self.parameters = parameters
        self.defaults = defaults
        self.body = body


class Return(BaseNode):
    def __init__(self, value):
        self.value: Expr | None = value


class AssertStatement(BaseNode):
    def __init__(self, test):
        self.test: Expr = test


class TrueNode(Expr):
    pass


class FalseNode(Expr):
    pass


class Nil:
    pass


class VariableDeclaration(BaseNode):
    def __init__(self, name, is_mutable):
        self.name: Name = name
        self.is_mutable: bool = is_mutable