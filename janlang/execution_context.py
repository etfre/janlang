class ExecutionContext:

    def __init__(self):
        self.scopes = []

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise RuntimeError(f'Missing name {name}')

    def add_scope(self):
        self.scopes.append({})

    def assign(self, name, value):
        self.scopes[-1][name] = value

# class Scope:

#     def __init__(self):
#         pass