from typing import Any
from values import base, function, class_definition
import astree as ast


class ClassInstance(base.BaseValue):

    def __init__(self, cls_def: class_definition.ClassDefinition) -> None:
        super().__init__()
        import environment
        self.cls_def = cls_def

    def instantiate(self):
        raise NotImplementedError