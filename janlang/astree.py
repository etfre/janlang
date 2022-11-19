from __future__ import annotations
import types
import re
import json
import operator
import execution_context
import interpreter
import function
from values.base import BaseValue
import values
from typing import List as ListType, TypeAlias


class BaseNode:
    pass


class Expr(BaseNode):
    pass


class Program(BaseNode):
    def __init__(self, main):
        self.main = main

    def execute(self, context):
        self.main.execute(context)

    def typecheck(self, context):
        pass


class Block(BaseNode):
    def __init__(self, statements):
        self.statements: ListType[BaseNode] = statements


class Module(BaseNode):
    def __init__(self, body):
        self.body = body


class ArgumentReference(BaseNode):
    def __init__(self, value: str):
        self.value = value

    def execute(self, context):
        return context.argument_frames[-1][self.value]


class Whitespace(BaseNode):
    def __init__(self, value: str):
        self.value = value

    def execute(self, context):
        return self.value


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


class Not(Expr):
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
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def execute(self, context):
        right = self.right.evaluate(context)
        return self.left.evaluate(context) ** right


class Or(Expr):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def execute(self, context):
        return self.left.evaluate(context) or self.right.evaluate(context)


class And(Expr):
    def __init__(self, left, right):
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
    def __init__(self, attribute_of, name):
        self.attribute_of = attribute_of
        self.name = name

    def typecheck(self):
        pass


class Index(Expr):
    def __init__(self, index_of, index):
        self.index_of = index_of
        self.index = index


class Slice(BaseNode):
    def __init__(self, slice_of, start, stop, step):
        self.slice_of: Expr = slice_of
        self.start = start
        self.stop = stop
        self.step = step


class Parameter(Expr):
    def __init__(self, name):
        self.name = name


class Call(Expr):
    def __init__(self, fn, args, kwargs):
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def prepare_call(self, context):
        function_to_call = self.fn.execute(context)
        arg_values = [arg.execute(context) for arg in self.args]
        kwarg_values = {k: v.execute(context) for k, v in self.kwargs.items()}
        return arg_values, kwarg_values, function_to_call


class Assignment(BaseNode):
    def __init__(self, left, right):
        self.left: BaseNode = left
        self.right: Expr = right


class WhileStatement(BaseNode):
    def __init__(self, test, body):
        self.test: Expr = test
        self.body: Block = body


class ForStatement(BaseNode):
    def __init__(self, left, iter, body):
        self.left = left
        self.iter = iter
        self.body: Block = body


class ContinueStatement(BaseNode):
    def execute(self, context: execution_context.ExecutionContext):
        raise interpreter.Continue()


class BreakStatement(BaseNode):
    def execute(self, context: execution_context.ExecutionContext):
        raise interpreter.Break()


class Name(BaseNode):
    def __init__(self, value):
        self.value: str = value


class FunctionDefinition(BaseNode):
    def __init__(self, name: str, parameters, defaults, body):
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
        self.value: Expr = value


class AssertStatement(BaseNode):
    def __init__(self, test):
        self.test: Expr = test


class TrueNode(BaseNode):
    pass


class FalseNode(BaseNode):
    pass


class Nil:
    pass


class VariableDeclaration(BaseNode):
    def __init__(self, name, is_mutable):
        self.name: Name = name
        self.is_mutable: bool = is_mutable
