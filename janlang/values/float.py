from values import base


class Float(base.BaseValue):
    def __init__(self, val) -> None:
        super().__init__(proxy=val)

    def __repr__(self) -> str:
        return str(self.proxy)
