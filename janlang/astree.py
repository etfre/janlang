import types
import re
import json
import operator
import execution_context
import interpreter
import interpreter
import function
import values


class BaseNode:
    
    def execute(self, context):
        print(type(self))
        raise NotImplementedError

    def typecheck(self, context):
        raise NotImplementedError

class Program(BaseNode):

    def __init__(self, main):
        self.main = main

    def execute(self, context):
        self.main.execute(context)

    def typecheck(self, context):
        pass

class Block(BaseNode):

    def __init__(self, statements):
        self.statements = statements

    def execute(self, context):
        for stmt in self.statements:
            stmt.execute(context)

class Module(BaseNode):

    def __init__(self, body):
        self.body = body

    def execute(self, context):
        for item in self.body:
            item.execute(context)

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

class String(BaseNode):

    def __init__(self, value: str):
        self.value = value

    def execute(self, context):
        return values.String(self.value)

class Integer(BaseNode):

    def __init__(self, value: int):
        self.value = int(value)

    def execute(self, context):
        return values.Integer(self.value)

class IfStatement:

    def __init__(self, test, orelse, body):
        self.test = test
        self.orelse = orelse
        self.body = body

    def execute(self, context):
        test_result = self.test.execute(context)
        if test_result:
            for stmt in self.body:
                stmt.execute(context)
        return test_result

class Float(BaseNode):

    def __init__(self, value: float):
        self.value = float(value)

    def execute(self, context):
        return values.Float(self.value)

class Not(BaseNode):
    def __init__(self, expr):
        self.expr = expr

class UnaryOp(BaseNode):

    def __init__(self, operation, operand):
        self.operation = operation
        self.operand = operand

    def execute(self, context):
        if self.operation == 'positive':
            return +(self.operand.evaluate(context))
        if self.operation == 'negative':
            return -(self.operand.evaluate(context))
        if self.operation == 'not':
            return not self.operand.evaluate(context)
        raise NotImplementedError

class BinOp(BaseNode):

    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def execute(self, context):
        return self.op.evaluate(context, self.left, self.right)

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

class Exponent(BaseNode):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def execute(self, context):
        right = self.right.evaluate(context)
        return self.left.evaluate(context) ** right

class Or(BaseNode):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def execute(self, context):
        return self.left.evaluate(context) or self.right.evaluate(context)

class And(BaseNode):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def execute(self, context):
        return self.left.evaluate(context) and self.right.evaluate(context)

class Compare(BaseNode):

    def __init__(self, left, ops, comparators):
        self.left = left
        self.ops = ops
        self.comparators = comparators

    def execute(self, context):
        # operator_map = {'!=': operator.ne, '==': operator.eq, '<': operator.lt, '<=': operator.le, '>': operator.gt, '>=': operator.ge}
        curr = self.left.execute(context)
        for op, node in zip(self.ops, self.comparators):
            right = node.execute(context)
            if not op.evaluate(context, curr, right):
                return False
            curr = right
        return True

class List(BaseNode):

    def __init__(self, items):
        self.items = items

    def execute(self, context):
        return values.List([x.execute(context) for x in self.items])

class Attribute(BaseNode):

    def __init__(self, attribute_of, name):
        self.attribute_of = attribute_of
        self.name = name

    def execute(self, context):
        attribute_of_value = self.attribute_of.execute(context)
        return getattr(attribute_of_value, self.name)

    def typecheck(self):
        pass

class Index(BaseNode):

    def __init__(self, index_of, index):
        self.index_of = index_of
        self.index = index

    def execute(self, context):
        index_of_value = self.index_of.execute(context)
        index = self.index.execute(context)
        return index_of_value[index]

class Slice(BaseNode):

    def __init__(self, slice_of, start, stop, step):
        self.slice_of = slice_of
        self.start = start
        self.stop = stop
        self.step = step

    def execute(self, context):
        slice_of_value = self.slice_of.execute(context)
        start = None if self.start is None else self.start.execute(context)
        stop = None if self.stop is None else self.stop.execute(context)
        step = None if self.step is None else self.step.execute(context)
        return slice_of_value[start:stop:step]

class Parameter(BaseNode):

    def __init__(self, name):   
        self.name = name

class Call(BaseNode):

    def __init__(self, fn, args, kwargs):
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def prepare_call(self, context):
        function_to_call = self.fn.execute(context)
        arg_values = [arg.execute(context) for arg in self.args]
        kwarg_values = {k: v.execute(context) for k, v in self.kwargs.items()}
        return arg_values, kwarg_values, function_to_call

    def execute(self, context: execution_context.ExecutionContext):
        function_to_call = self.fn.execute(context)
        if not isinstance(function_to_call, function.Function):
            raise RuntimeError(f'Trying to call a function, but got {function_to_call}')
        return function_to_call.call(context, self.args, self.kwargs)

class Assignment(BaseNode):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def execute(self, context: execution_context.ExecutionContext):
        name_string = self.left.value
        symbol = context.symbol_lookup(name_string)
        value = self.right.execute(context)
        context.assign(name_string, value)

class WhileStatement(BaseNode):

    def __init__(self, test, body):
        self.test = test
        self.body = body

    def execute(self, context: execution_context.ExecutionContext):
        while self.test.execute(context):
            for stmt in self.body:
                try:
                    stmt.execute(context)
                except interpreter.Continue:
                    break
                except interpreter.Break:
                    return

class ForStatement(BaseNode):

    def __init__(self, left, iter, body):
        self.left = left
        self.iter = iter
        self.body = body

    def execute(self, context: execution_context.ExecutionContext):
        name_string = self.left.value
        symbol = context.symbol_lookup(name_string)
        value = self.right.execute(context)
        context.assign(name_string, value)

class ContinueStatement(BaseNode):

    def execute(self, context: execution_context.ExecutionContext):
        raise interpreter.Continue()

class BreakStatement(BaseNode):

    def execute(self, context: execution_context.ExecutionContext):
        raise interpreter.Break()

class Name(BaseNode):

    def __init__(self, value):
        self.value = value

    def execute(self, context):
        return context.symbol_lookup(self.value).value

class FunctionDefinition(BaseNode):

    def __init__(self, name: str, parameters, defaults, body):
        self.name = name
        self.parameters = parameters
        self.defaults = defaults
        self.body = body

    def execute(self, context: execution_context.ExecutionContext):
        fn = function.Function(self.name, self.parameters, self.defaults, self.body)
        context.declare(self.name, 'function')
        context.assign(self.name, fn)
    
class ClassDefinition(BaseNode):

    def __init__(self, name: str, parameters, defaults, body):
        self.name = name
        self.parameters = parameters
        self.defaults = defaults
        self.body = body

    def execute(self, context: execution_context.ExecutionContext):
        fn = function.Function(self.name, self.parameters, self.defaults, self.body)
        context.declare(self.name, 'function')
        context.assign(self.name, fn)
    
class Return(BaseNode):

    def __init__(self, value):
        self.value = value

    def execute(self, context):
        result = self.value.execute(context)
        raise function.Return(result)

class AssertStatement(BaseNode):

    def __init__(self, test):
        self.test = test

class TrueNode(BaseNode):
    pass

class FalseNode(BaseNode):
    pass

class Nil:
    pass

class VariableDeclaration(BaseNode):

    def __init__(self, name, is_mutable):
        self.name = name
        self.is_mutable = is_mutable

    def execute(self, context: execution_context.ExecutionContext):
        name = self.name.value
        decl_type = 'variable' if self.is_mutable else 'immutable_variable'
        context.declare(name, decl_type)