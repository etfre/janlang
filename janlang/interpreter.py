import execution_context

class Interpreter:

    def __init__(self):
        pass

    def execute(self, root):
        context = execution_context.ExecutionContext()
        context.add_scope()
        root.execute(context)