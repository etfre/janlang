from values import base


class Boolean(base.BaseValue):
    def __init__(self, val: bool) -> None:
        self._val = val

    def __repr__(self) -> str:
        return str(self._val)

    def __bool__(self):
        return self._val
