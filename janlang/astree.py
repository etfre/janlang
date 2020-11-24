import types
import re
import json
import operator
import execution_context
import interpreter
import interpreter
import function
import data_structures

class BaseActionNode:
    
    def execute(self, context):
        print(type(self))
        raise NotImplementedError

class Module(BaseActionNode):

    def __init__(self, body):
        self.body = body

    def execute(self, context):
        for item in self.body:
            item.execute(context)

class Literal(BaseActionNode):
    
    def __init__(self, value: str):
        self.value = value

    def execute(self, context):
        return self.value

class ArgumentReference(BaseActionNode):

    def __init__(self, value: str):
        self.value = value

    def execute(self, context):
        return context.argument_frames[-1][self.value]

class Whitespace(BaseActionNode):

    def __init__(self, value: str):
        self.value = value

    def execute(self, context):
        return self.value

class ExprSequenceSeparator(BaseActionNode):

    def __init__(self, value: str):
        self.value = value

    def execute(self, context):
        return None

class Gt(BaseActionNode):
    
    def evaluate(self, context, left, right):
        return left > right

class GtE(BaseActionNode):
    
    def evaluate(self, context, left, right):
        return left >= right

class Lt(BaseActionNode):

    def evaluate(self, context, left, right):
        return left < right

class LtE(BaseActionNode):
    
    def evaluate(self, context, left, right):
        return left <= right

class Eq(BaseActionNode):

    def evaluate(self, context, left, right):
        return left == right

class NotEq(BaseActionNode):
    
    def evaluate(self, context, left, right):
        return left != right

class String(BaseActionNode):

    def __init__(self, value: str):
        self.value = value

    def execute(self, context):
        return self.value

class Integer(BaseActionNode):

    def __init__(self, value: int):
        self.value = int(value)

    def execute(self, context):
        return self.value

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

class Float(BaseActionNode):

    def __init__(self, value: float):
        self.value = float(value)

    def execute(self, context):
        return self.value

class UnaryOp(BaseActionNode):

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

class BinOp(BaseActionNode):

    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

    def execute(self, context):
        return self.op.evaluate(context, self.left, self.right)

class Add(BaseActionNode):
    
    def evaluate(self, context, left, right):
        return left.execute(context) + right.execute(context)

class Subtract(BaseActionNode):
    def evaluate(self, context, left, right):
        return left.execute(context) - right.execute(context)

        
class Multiply(BaseActionNode):
    def evaluate(self, context, left, right):
        return left.execute(context) * right.execute(context)

class Divide(BaseActionNode):
    def evaluate(self, context, left, right):
        return left.execute(context) / right.execute(context)

class Exponent(BaseActionNode):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def execute(self, context):
        right = self.right.evaluate(context)
        return self.left.evaluate(context) ** right

class Or(BaseActionNode):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def execute(self, context):
        return self.left.evaluate(context) or self.right.evaluate(context)

class And(BaseActionNode):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def execute(self, context):
        return self.left.evaluate(context) and self.right.evaluate(context)

class Compare(BaseActionNode):

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

class List(BaseActionNode):

    def __init__(self, items):
        self.items = items

    def execute(self, context):
        vals = [x.execute(context) for x in self.items]
        l = data_structures.List(vals)
        return l

class Attribute(BaseActionNode):

    def __init__(self, attribute_of, name):
        self.attribute_of = attribute_of
        self.name = name

    def execute(self, context):
        attribute_of_value = self.attribute_of.execute(context)
        return getattr(attribute_of_value, self.name)

class Index(BaseActionNode):

    def __init__(self, index_of, index):
        self.index_of = index_of
        self.index = index

    def execute(self, context):
        index_of_value = self.index_of.execute(context)
        index = self.index.execute(context)
        return index_of_value[index]

class Slice(BaseActionNode):

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

class Parameter(BaseActionNode):

    def __init__(self, name):   
        self.name = name

class Call(BaseActionNode):

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

class Assignment(BaseActionNode):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def execute(self, context: execution_context.ExecutionContext):
        name_string = self.left.value
        symbol = context.symbol_lookup(name_string)
        value = self.right.execute(context)
        context.assign(name_string, value)

class WhileStatement(BaseActionNode):

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

class ForStatement(BaseActionNode):

    def __init__(self, target, iter, body):
        self.target = target
        self.iter = iter
        self.body = body

    def execute(self, context: execution_context.ExecutionContext):
        name_string = self.target.value
        context.add_scope()
        context.declare(name_string)

class ContinueStatement(BaseActionNode):

    def execute(self, context: execution_context.ExecutionContext):
        raise interpreter.Continue()

class BreakStatement(BaseActionNode):

    def execute(self, context: execution_context.ExecutionContext):
        raise interpreter.Break()

class Name(BaseActionNode):

    def __init__(self, value, ctx):
        self.value = value
        self.ctx = ctx

    def execute(self, context):
        return context.symbol_lookup(self.value).value

class FunctionDefinition(BaseActionNode):

    def __init__(self, name: str, parameters, defaults, body):
        self.name = name
        self.parameters = parameters
        self.defaults = defaults
        self.body = body

    def execute(self, context: execution_context.ExecutionContext):
        fn = function.Function(self.name, self.parameters, self.defaults, self.body)
        context.declare(self.name, 'function')
        context.assign(self.name, fn)
    
class Return(BaseActionNode):

    def __init__(self, value):
        self.value = value

    def execute(self, context):
        result = self.value.execute(context)
        raise function.Return(result)

class Variable(BaseActionNode):

    def __init__(self, value):
        self.value = value

    def execute(self, context):
        index = self.value - 1 if self.value > 0 else self.value
        try:
            action = context.variables[index]
        except IndexError:
            return
        return action.evaluate(context)

class RegularExpression(BaseActionNode):
    
    def __init__(self, value):
        self.value = value

    def execute(self, context):
        return re.compile(self.value, flags=re.IGNORECASE)

class Nil:
    pass

class VariableDeclaration(BaseActionNode):

    def __init__(self, name, is_mutable):
        self.name = name
        self.is_mutable = is_mutable

    def execute(self, context: execution_context.ExecutionContext):
        name = self.name.value
        decl_type = 'variable' if self.is_mutable else 'immutable_variable'
        context.declare(name, decl_type)

class Store(BaseActionNode):
    pass

class Assign(BaseActionNode):
    pass

class Del(BaseActionNode):
    pass