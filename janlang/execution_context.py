class ExecutionContext:

    def __init__(self):
        self._scopes = []

    def symbol_lookup(self, name):
        for scope in reversed(self._scopes):
            if name in scope.symbols:
                symbol = scope.symbols[name]
                return symbol
        raise RuntimeError(f'Missing name {name}')

    def add_scope(self):
        scope = Scope()
        self._scopes.append(scope)
        return scope

    def remove_scope(self):
        return self._scopes.pop()

    def assign(self, name, value):
        symbol = self.symbol_lookup(name)
        if symbol.value_initialized and symbol.type == 'immutable_variable':
            raise RuntimeError(f'Cannot redeclare variable {name}')
        symbol.value = value
        symbol.value_initialized = True

    def declare(self, name, type):
        symbols = self._scopes[-1].symbols
        if name in symbols:
            raise RuntimeError('Cannot redeclare variable in the same scope')
        symbol = Symbol(name, type)
        symbols[name] = symbol

class Scope:

    def __init__(self):
        self.symbols = {}

class Symbol:

    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.value = None
        self.value_initialized = False