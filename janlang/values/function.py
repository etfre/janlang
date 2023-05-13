import environment
import values

class Function(values.BaseValue):

    def __init__(self, name: str, parameters, defaults, body, closure, is_native_function: bool):
        super().__init__()
        self.name = name
        self.parameters = parameters
        self.defaults = defaults
        self.body = body
        self.closure: environment.Environment = closure
        self.is_native_function = is_native_function

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