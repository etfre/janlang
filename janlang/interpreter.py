import execution_context
import native_functions
import function

class Interpreter:

    def __init__(self):
        pass

    def execute(self, root):
        context = execution_context.ExecutionContext()
        context.add_scope()
        self.add_native_functions(context)
        root.execute(context)

    def add_native_functions(self, context: execution_context.ExecutionContext):
        for name, native_fn in native_functions.FUNCTIONS.items():
            fn = function.Function(name, [], [], native_fn)
            context.declare(name, 'native_function')
            context.assign(name, fn)