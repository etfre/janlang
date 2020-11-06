import execution_context

class Function:

    def __init__(self, name: str, parameters, defaults, action):
        self.name = name
        self.parameters = parameters
        self.defaults = defaults
        self.action = action 

    def call(self, context: execution_context.ExecutionContext, args, kwargs):
        arg_values = [arg.execute(context) for arg in args]
        kwarg_values = {k: v.execute(context) for k, v in kwargs.items()}
        result = None
        context.add_scope()
        if isinstance(self.action, list):
            for i, param in enumerate(self.parameters):
               context.assign(param.name, arg_values[i])
            for statement in self.action:
                try:
                    statement.execute(context)
                except Return as e:
                    result = e.value
                    break
        else:
            result = self.action(context, *arg_values, **kwarg_values)
        context.remove_scope()
        return result

class Return(BaseException):
    
    def __init__(self, value):
        self.value = value