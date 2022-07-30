import contextlib
import execution_context
import native_functions
import function
import astree as ast
import environment, values

class Interpreter:

    def __init__(self):
        self.execute_map = {
            ast.Program: self.execute_program,
            ast.Module: self.execute_module,
            ast.VariableDeclaration: self.execute_variable_declaration,
            ast.Assignment: self.execute_assignment,
            ast.String: self.execute_string,
            ast.IfStatement: self.execute_if_statement,
            ast.Block: self.execute_block,
            ast.Name: self.execute_name,
            ast.Integer: self.execute_integer,
            ast.Call: self.execute_call,
            ast.FunctionDefinition: self.execute_function_definition,
            ast.Return: self.execute_return,
            ast.BinOp: self.execute_bin_op,
            ast.Compare: self.execute_compare,
        }
        self.environment = environment.Environment(parent=None)
        self.setup_globals()


    def execute(self, node):
        fn = self.execute_map[type(node)]
        return fn(node)

    def execute_module(self, module: ast.Module):
        for stmt in module.body:
            self.execute(stmt)

    def execute_variable_declaration(self, vardec: ast.VariableDeclaration):
        name = vardec.name.value
        decl_type = 'variable' if vardec.is_mutable else 'immutable_variable'
        self.environment.declare(name, decl_type)

    def execute_assignment(self, assgn: ast.Assignment):
        name_string = assgn.left.value
        symbol = self.environment.get(name_string)
        value = self.execute(assgn.right)
        self.environment.assign(name_string, value)

    def execute_name(self, name: ast.Name):
        return self.environment.get(name.value).value

    def execute_string(self, str_: ast.String) -> values.String:
        return values.String(str_.value)

    def execute_compare(self, cmp: ast.Compare) -> values.String:
        # operator_map = {'!=': operator.ne, '==': operator.eq, '<': operator.lt, '<=': operator.le, '>': operator.gt, '>=': operator.ge}
        curr = self.execute(cmp.left)
        for op, node in zip(cmp.ops, cmp.comparators):
            right = self.execute(node)
            if not op.evaluate(curr, right):
                return False
            curr = right
        return True
        # cmp.
        return values.String(str_.value)

    def execute_call(self, call: ast.Call) -> values.String:
        function_to_call = self.execute(call.fn)
        if not isinstance(function_to_call, function.Function):
            raise RuntimeError(f'Trying to call a function, but got {function_to_call}')
        args = [self.execute(arg) for arg in call.args]
        kwargs = {k: self.execute(v) for k, v in call.kwargs.items()}
        # env = environment.Environment(self.closure)
        return function_to_call.call(self, args, kwargs)
        args = [self.execute(arg) for arg in call.args]
        kwargs = {k: self.execute(v) for k, v in call.kwargs.items()}
        result = None
        # context.add_scope()
        if isinstance(self.action, list):
            for i, param in enumerate(self.parameters):
               context.declare(param.name, 'parameter')
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
        # return function_to_call.call(context, self.args, self.kwargs)

    def execute_integer(self, int_: ast.Integer) -> values.String:
        return values.Integer(int_.value)

    def execute_if_statement(self, if_statement: ast.String):
        test_result = self.execute(if_statement.test)
        if test_result:
            self.execute(if_statement.body)

    def execute_function_definition(self, definition: ast.Block):
        fn = function.Function(definition.name, definition.parameters, definition.defaults, definition.body, self.environment, False)
        self.environment.declare(definition.name, 'function')
        self.environment.assign(definition.name, fn)

    def execute_block(self, block: ast.Block, env=None):
        previous = self.environment
        self.environment = environment.Environment(previous) if env is None else env
        try:
            for stmt in block.statements:
                self.execute(stmt)
        finally:
            self.environment = previous

    def execute_return(self, ret):
        result = self.execute(ret.value)
        raise function.Return(result)

    def execute_bin_op(self, bin_op: ast.BinOp):
        left, right = self.execute(bin_op.left), self.execute(bin_op.right)
        return bin_op.op.evaluate(left, right)

    def execute_program(self, program: ast.Program):
        return self.execute(program.main)

    def setup_globals(self):
        closure = self.environment
        is_native_function = True
        for name, native_fn in native_functions.FUNCTIONS.items():
            fn = function.Function(name, [], [], native_fn, closure, is_native_function)
            self.environment.declare(name, 'native_function')
            self.environment.assign(name, fn)

class Continue(BaseException):
    pass

class Break(BaseException):
    pass