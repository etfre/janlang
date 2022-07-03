from values import base

class String(base.BaseValue):
    def __init__(self, val) -> None:
        self._val = val
    def __repr__(self) -> str:
       return self._val