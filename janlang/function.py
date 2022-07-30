import execution_context, environment

class Function:

    def __init__(self, name: str, parameters, defaults, body, closure, is_native_function):
        self.name = name
        self.parameters = parameters
        self.defaults = defaults
        self.body = body
        self.closure = closure
        self.is_native_function = is_native_function

    def call(self, interpreter, args, kwargs):
        if self.is_native_function:
            return self.body(*args, **kwargs)
        env = environment.Environment(self.closure)
        for arg, param in zip(args, self.parameters):
            env.declare(param.name, 'parameter')
            env.assign(param.name, arg)
            print(arg, param, type(arg))
        # result = None
        try:
            interpreter.execute_block(self.body, env)
        except Return as ret:
            return ret.value
        # for 
        #     interpreter.execute_block(self.body)
        #     for i, param in enumerate(self.parameters):
        #        context.declare(param.name, 'parameter')
        #        context.assign(param.name, args[i])
        #     for statement in self.body:
        #         try:
        #             statement.execute(context)
        #         except Return as e:
        #             result = e.value
        #             break
        # else:
        #     result = self.body(context, *args, **kwargs)
        # context.remove_scope()
        # return result

class Return(BaseException):
    
    def __init__(self, value):
        self.value = value