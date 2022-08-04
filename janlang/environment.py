from __future__ import annotations
from values import base

class Environment:

    def __init__(self, parent) -> None:
        self.values = {}
        self.parent = parent

    def declare(self, name: str, type_) -> Symbol:
        if name in self.values:
            raise RuntimeError(f'{name} already declared in this scope')
        symbol = Symbol(name, type_)
        self.values[name] = symbol
        return symbol

    def assign(self, name: str, value: base.BaseValue) -> Symbol:
        assert value is not None
        symbol = self.get(name)
        if symbol.type == "immutable_variable" and symbol.value_initialized:
            raise RuntimeError(f'Cannot reassign to immutable variable {name}')
        symbol.value = value
        symbol.value_initialized = True
        return symbol
        
    def get(self, name: str) -> Symbol:
        if name not in self.values:
            if self.parent is None:
                raise RuntimeError(f'{name} not in environment')
            return self.parent.get(name)
        return self.values[name]

class Symbol:

    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.value = None
        self.value_initialized = False