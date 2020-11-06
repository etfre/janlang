import execution_context

class Function:

    def __init__(self, name: str, parameters, defaults, action):
        self.name = name
        self.parameters = parameters
        self.defaults = defaults
        self.action = action 

    def call(self, context: execution_context.ExecutionContext, arg_ast, kwarg_ast):
        args = [arg.execute(context) for arg in arg_ast]
        kwargs = {k: v.execute(context) for k, v in kwarg_ast.items()}
        result = None
        context.add_scope()
        if isinstance(self.action, list):
            for i, param in enumerate(self.parameters):
               context.assign(param.name, args[i])
            for statement in self.action:
                try:
                    statement.execute(context)
                except Return as e:
                    result = e.value
                    break
        else:
            result = self.action(context, *args, **kwargs)
        context.remove_scope()
        return result

class Return(BaseException):
    
    def __init__(self, value):
        self.value = value