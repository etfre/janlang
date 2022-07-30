from values import base


class Float(base.BaseValue):
    def __init__(self, val) -> None:
        self._val = val

    def __repr__(self) -> str:
        return str(self._val)