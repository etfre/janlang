import environment
import inspect
import values
import astree as ast
from typing import Any, Callable

class NativeFunction(values.BaseValue):
    
    def __init__(self, name: str, fn) -> None:
        super().__init__()
        self.name = name
        self.fn = fn

    def call(self, args, kwargs):
        return self.fn(*args, **kwargs)

class Function(values.BaseValue):

    def __init__(self, name: str, parameters: list[ast.Parameter], defaults, body: ast.Block | Callable, closure):
        super().__init__()
        self.name = name
        self.parameters = parameters
        self.defaults = defaults
        self.body = body
        self.closure: environment.Environment = closure

    @classmethod
    def from_ast(cls, func_ast: ast.FunctionDefinition, closure):
        return cls(func_ast.name, func_ast.parameters, func_ast.defaults, func_ast.body, closure)

    def call(self, interpreter, args, kwargs):
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