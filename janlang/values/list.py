from values import base


class List(base.BaseValue):
    proxy: list
    def __init__(self, l: list) -> None:
        super().__init__(l)

    def __repr__(self) -> str:
        return str(self.proxy)

    def push(self, val):
        self.proxy.append(val)

    def pop(self):
        return self.proxy.pop()