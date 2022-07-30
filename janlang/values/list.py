from values import base


class List(base.BaseValue):
    def __init__(self, l) -> None:
        self._list = l

    def __repr__(self) -> str:
        return str(self._list)

    def __getitem__(self, i):
        return self._list[i._val]

    def push(self, val):
        self._list.append(val)

    def pop(self):
        return self._list.pop()