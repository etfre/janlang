from values import base, float

class Integer(base.BaseValue):
    def __init__(self, val) -> None:
        super().__init__(val)

    def __repr__(self) -> str:
        return str(self.proxy)