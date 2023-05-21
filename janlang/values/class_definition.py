from typing import Any
from values import base, function
import astree as ast


class ClassDefinition(base.BaseValue):

    def __init__(self, name: str, methods: list[function.Function], closure) -> None:
        super().__init__()
        import environment
        self.name = name
        self.methods = {method.name: method for method in methods}
        self.closure: environment.Environment = closure

    def instantiate(self):
        raise NotImplementedError