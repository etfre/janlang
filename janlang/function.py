import execution_context

class Function:

    def __init__(self, name: str, parameters, action):
        self.name = name
        self.parameters = parameters
        self.action = action 

    def call(self, context: execution_context.ExecutionContext, args, kwargs):
        arg_values = [arg.execute(context) for arg in args]
        kwarg_values = {k: v.execute(context) for k, v in kwargs.items()}
        context.add_scope()
        if isinstance(self.action, list):
            for statement in self.action:
                raise NotImplementedError
        else:
            result = self.action(context, *arg_values, **kwarg_values)
        context.remove_scope()
        return result