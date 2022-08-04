from values import base


class Boolean(base.BaseValue):
    def __init__(self, val) -> None:
        if val not in (True, False):
            val = bool(val)
        super().__init__(val)

    def __repr__(self) -> str:
        return str(self.proxy)
    