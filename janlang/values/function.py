import environment
import values
import astree as ast
from typing import Callable

class Function(values.BaseValue):

    def __init__(self, name: str, parameters: list[ast.Parameter], defaults, body: ast.Block | Callable, closure):
        import native_functions
        super().__init__()
        self.name = name
        self.parameters = parameters
        self.defaults = defaults
        if not isinstance(body, ast.Block):
            assert body in native_functions.INVERTED_FUNCTIONS
        self.body = body
        self.closure: environment.Environment = closure
        self.is_native_function = body in native_functions.INVERTED_FUNCTIONS

    @classmethod
    def from_ast(cls, func_ast: ast.FunctionDefinition, closure):
        return cls(func_ast.name, func_ast.parameters, func_ast.defaults, func_ast.body, closure)

    def call(self, interpreter, args, kwargs):
        if self.is_native_function:
            return self.body(*args, **kwargs)
        env = self.closure.add_child()
        for arg, param in zip(args, self.parameters):
            env.declare(param.name, 'parameter')
            env.assign(param.name, arg)
        try:
            interpreter.execute_block(self.body, env)
        except Return as ret:
            return ret.value
        return values.Void()

class Return(BaseException):
    
    def __init__(self, value: values.BaseValue):
        self.value = value