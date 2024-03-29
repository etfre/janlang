from __future__ import annotations
from values import base, Void
from typing import Literal


DECLARATION_TYPE = Literal["function", "native_function", "parameter", "immutable_variable", "variable", "class_definition"]

class Environment:

    def __init__(self, parent: Environment | None) -> None:
        self.values: dict[str, Symbol] = {}
        self.parent = parent

    @property
    def is_root(self):
        return self.parent is None

    def declare(self, name: str, type_: DECLARATION_TYPE) -> Symbol:
        if name in self.values:
            raise RuntimeError(f'{name} already declared in this scope')
        symbol = Symbol(name, type_)
        self.values[name] = symbol
        return symbol

    def assign(self, name: str, value: base.BaseValue) -> Symbol:
        assert value is not None
        if isinstance(value, Void):
            raise RuntimeError("Cannot assign void type")
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

    def deep_copy(self):
        if self.parent is None:
            return self
        copied_parent = self.parent.deep_copy()
        copied = Environment(copied_parent)
        copied.values = self.values.copy()
        return copied

    def add_child(self):
        parent = self.deep_copy()
        new_env = Environment(parent)
        return new_env

class Symbol:

    def __init__(self, name: str, type: DECLARATION_TYPE):
        self.name = name
        self.type = type
        self.value: base.BaseValue | None = None
        self.value_initialized: bool = False