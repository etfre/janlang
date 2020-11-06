import types
import re
import json
import operator
import execution_context
import function

def evaluate_generator(gen):
    assert isinstance(gen, types.GeneratorType)
    last = None
    for node, item in exhaust_generator(gen):
        last = item
    return last

def exhaust_generator(gen):
    assert isinstance(gen, types.GeneratorType)
    for item in gen:
        if isinstance(item, types.GeneratorType):
            yield from exhaust_generator(item)
        else:
            yield item

class BaseActionNode:
    
    def execute(self, context):
        print(type(self))
        raise NotImplementedError

    def evaluate_lazy(self, context):
        yield self, self.evaluate(context)

    def evaluate_without_context(self):
        import recognition.actions.context
        context = recognition.actions.context.empty_recognition_context() 
        return self.evaluate(context)

    def perform(self, context):
        context.argument_frames.append({})
        gen = self.evaluate_lazy(context)
        evaluated_nodes = []
        written_nodes = []
        for i, (node, result) in enumerate(self.evaluate_lazy(context)):
            assert isinstance(node, BaseActionNode)
            evaluated_nodes.append(node)
        context.argument_frames.pop()

class Module(BaseActionNode):

    def __init__(self, body):
        self.body = body

    def execute(self, context):
        print(self.body)
        for item in self.body:
            item.execute(context)

class ExpressionSequence(BaseActionNode):

    def __init__(self, expressions):
        self.expressions = expressions

    def execute(self, context):
        evaluated_nodes = []
        last = None
        for i, expr in enumerate(self.expressions):
            if isinstance(expr, Literal) and i > 1:
                second_previous, previous = self.expressions[i - 2:i]
                if isinstance(second_previous, Literal) and isinstance(previous, ExprSequenceSeparator):
                    last += previous.value
            result = expr.evaluate(context)
            if isinstance(last, str) and isinstance(result, str):
                last += result
            elif result is not None:
                last = result
        return last

    def evaluate_lazy(self, context):
        for expr in self.expressions:
            yield from exhaust_generator(expr.evaluate_lazy(context))

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
    pass

class GtE(BaseActionNode):
    pass

class Lt(BaseActionNode):
    pass

class LtE(BaseActionNode):
    pass

class Eq(BaseActionNode):
    pass

class NotEq(BaseActionNode):
    pass

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

    def __init__(self, test, body):
        self.test = test
        self.body = body

    def execute(self, context):
        test_result = self.test.execute(context)
        if test_result:
            for stmt in self.body:
                stmt.execute(context)

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
        operator_map = {'!=': operator.ne, '==': operator.eq, '<': operator.lt, '<=': operator.le, '>': operator.gt, '>=': operator.ge}
        curr = self.left.evaluate(context)
        for op, node in zip(self.ops, self.comparators):
            op_func = operator_map[op]
            right = node.evaluate(context)
            if not op_func(curr, right):
                return False
            curr = right
        return True

class List(BaseActionNode):

    def __init__(self, items):
        self.items = items

    def execute(self, context):
        return [x.evaluate(context) for x in self.items]

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

    def execute(self, context):
        name_string = self.left.value
        value = self.right.execute(context)
        context.assign(name_string, value)

class Name(BaseActionNode):

    def __init__(self, value):
        self.value = value

    def execute(self, context):
        return context.lookup(self.value)

class FunctionDefinition(BaseActionNode):

    def __init__(self, name: str, parameters, defaults, body):
        self.name = name
        self.parameters = parameters
        self.defaults = defaults
        self.body = body

    def execute(self, context: execution_context.ExecutionContext):
        fn = function.Function(self.name, self.parameters, self.defaults, self.body)
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

    def evaluate_lazy(self, context):
        index = self.value - 1 if self.value > 0 else self.value
        try:
            action = context.variables[index]
        except IndexError:
            return
        yield from exhaust_generator(action.evaluate_lazy(context))

class RegularExpression(BaseActionNode):
    
    def __init__(self, value):
        self.value = value

    def execute(self, context):
        return re.compile(self.value, flags=re.IGNORECASE)

class Nil:
    pass