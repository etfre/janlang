class ExecutionContext:

    def __init__(self):
        self._scopes = []

    def lookup(self, name):
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        raise RuntimeError(f'Missing name {name}')

    def add_scope(self):
        scope = {}
        self._scopes.append(scope)
        return scope

    def remove_scope(self):
        return self._scopes.pop()

    def assign(self, name, value):
        self._scopes[-1][name] = value

# class Scope:

#     def __init__(self):
#         pass