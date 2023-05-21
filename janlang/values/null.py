from values import base


class Null(base.BaseValue):
    def __init__(self) -> None:
        super().__init__(proxy=None)

    def __repr__(self) -> str:
        return str(self.proxy)
    