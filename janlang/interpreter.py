import contextlib
from xmlrpc.client import Boolean
import native_functions
import function
import astree as ast
import environment, values, errors


class Interpreter:
    def __init__(self):
        self.execute_map = {
            ast.AssertStatement: self.execute_assert_statement,
            ast.Assignment: self.execute_assignment,
            ast.BinOp: self.execute_bin_op,
            ast.Block: self.execute_block,
            ast.BreakStatement: self.execute_break_statement,
            ast.Call: self.execute_call,
            ast.Compare: self.execute_compare,
            ast.ContinueStatement: self.execute_continue_statement,
            ast.Dictionary: self.execute_dictionary,
            ast.FalseNode: self.execute_false,
            ast.Float: self.execute_float,
            ast.ForStatement: self.execute_for_statement,
            ast.FunctionDefinition: self.execute_function_definition,
            ast.IfStatement: self.execute_if_statement,
            ast.Index: self.execute_index,
            ast.Integer: self.execute_integer,
            ast.List: self.execute_list,
            ast.Module: self.execute_module,
            ast.Name: self.execute_name,
            ast.Negative: self.execute_negative,
            ast.Not: self.execute_not,
            ast.Program: self.execute_program,
            ast.Return: self.execute_return,
            ast.String: self.execute_string,
            ast.TrueNode: self.execute_true,
            ast.VariableDeclaration: self.execute_variable_declaration,
            ast.WhileStatement: self.execute_while_statement,
        }
        self.environment = environment.Environment(parent=None)
        self.setup_globals()

    def execute(self, node):
        fn = self.execute_map[type(node)]
        result = fn(node)
        print(result)
        assert result is None or isinstance(result, (values.BaseValue, function.Function))
        return result

    def execute_module(self, module: ast.Module):
        for stmt in module.body:
            self.execute(stmt)

    def execute_assert_statement(self, assert_statement: ast.AssertStatement):
        if not self.execute(assert_statement.test):
            print('raising assert')
            raise errors.JanAssertionError()

    def execute_list(self, list_: ast.List):
        return values.List([self.execute(x) for x in list_.items])

    def execute_dictionary(self, dict_: ast.Dictionary):
        py_dict = {}
        return values.Dictionary(py_dict)

    def execute_index(self, idx: ast.Index):
        index_of_value = self.execute(idx.index_of)
        index = self.execute(idx.index)
        return index_of_value[index]

    def execute_while_statement(self, while_statement: ast.WhileStatement):
        while self.execute(while_statement.test):
            try:
                self.execute(while_statement.body)
            except Continue:
                pass
            except Break:
                return

    def execute_for_statement(self, for_statement: ast.ForStatement):
        iter_obj = self.execute(for_statement.iter)
        for obj in iter_obj:
            env = self.environment.add_child()
            if isinstance(for_statement.left, ast.VariableDeclaration):
                decl_type = "variable" if for_statement.left.is_mutable else "immutable_variable"
                name = for_statement.left.name
                env.declare(name.value, decl_type)
            else:
                name = for_statement.left
            assert isinstance(name, ast.Name)
            env.assign(name.value, obj)
            try:
                self.execute_block(for_statement.body, env)
            except Continue:
                pass
            except Break:
                return

    def execute_break_statement(self, break_statement: ast.BreakStatement):
        raise Break()

    def execute_continue_statement(self, continue_statement: ast.ContinueStatement):
        raise Continue()

    def execute_variable_declaration(self, vardec: ast.VariableDeclaration):
        name = vardec.name.value
        decl_type = "variable" if vardec.is_mutable else "immutable_variable"
        self.environment.declare(name, decl_type)

    def execute_assignment(self, assgn: ast.Assignment):
        left = assgn.left
        if isinstance(left, ast.Name):
            name_string = left.value
            symbol = self.environment.get(name_string)
            value = self.execute(assgn.right)
            self.environment.assign(name_string, value)
        elif isinstance(left, ast.Index):
            index_of_value = self.execute(left.index_of)
            index_value = self.execute(left.index)
            index_of_value[index_value] = self.execute(assgn.right)
        elif isinstance(left, ast.Attribute):
            attribute_of_value = self.execute(left.attribute_of)
            attribute_name = self.execute(left.name)
            attribute_of_value[attribute_name] = self.execute(assgn.right)
        else:
            raise RuntimeError()

    def execute_name(self, name: ast.Name):
        return self.environment.get(name.value).value

    def execute_string(self, str_: ast.String) -> values.String:
        return values.String(str_.value)

    def execute_compare(self, cmp: ast.Compare) -> values.Boolean:
        # operator_map = {'!=': operator.ne, '==': operator.eq, '<': operator.lt, '<=': operator.le, '>': operator.gt, '>=': operator.ge}
        curr = self.execute(cmp.left)
        for op, node in zip(cmp.ops, cmp.comparators):
            right = self.execute(node)
            if not op.evaluate(curr, right):
                return values.Boolean(False)
            curr = right
        return values.Boolean(True)

    def execute_call(self, call: ast.Call) -> values.String:
        function_to_call = self.execute(call.fn)
        if not isinstance(function_to_call, function.Function):
            raise RuntimeError(f"Trying to call a function, but got {function_to_call}")
        args = [self.execute(arg) for arg in call.args]
        kwargs = {k: self.execute(v) for k, v in call.kwargs.items()}
        # env = environment.Environment(self.closure)
        return function_to_call.call(self, args, kwargs)
       
    def execute_integer(self, int_: ast.Integer) -> values.Integer:
        return values.Integer(int_.value)

    def execute_float(self, float_: ast.Float) -> values.Float:
        return values.Float(float_.value)

    def execute_true(self, node: ast.TrueNode) -> values.Boolean:
        return values.Boolean(True)

    def execute_false(self, node: ast.FalseNode) -> values.Boolean:
        return values.Boolean(False)

    def execute_if_statement(self, if_statement: ast.IfStatement):
        test_result = self.execute(if_statement.test)
        if test_result:
            self.execute(if_statement.body)

    def execute_not(self, not_expr: ast.Not):
        expr_result = self.execute(not_expr.expr)
        return Boolean(expr_result)

    def execute_negative(self, negative_expr: ast.Negative):
        expr_result = self.execute(negative_expr.value)
        return -expr_result

    def execute_function_definition(self, definition: ast.FunctionDefinition):
        closure = self.environment.deep_copy()
        fn = function.Function(
            definition.name,
            definition.parameters,
            definition.defaults,
            definition.body,
            closure,
            False,
        )
        self.environment.declare(definition.name, "function")
        self.environment.assign(definition.name, fn)
        if self.environment is not closure:
            #closure should know about function too for recursion
            closure.declare(definition.name, "function")
            closure.assign(definition.name, fn)

    def execute_block(self, block: ast.Block, env=None) -> None:
        previous = self.environment
        self.environment = previous.add_child() if env is None else env
        try:
            for stmt in block.statements:
                self.execute(stmt)
        finally:
            self.environment = previous

    def execute_return(self, ret: ast.Return):
        if ret.value is None:
            result = values.Void()
        else:
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
            self.environment.declare(name, "native_function")
            self.environment.assign(name, fn)


class Continue(BaseException):
    pass


class Break(BaseException):
    pass
