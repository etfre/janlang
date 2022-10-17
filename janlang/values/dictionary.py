from values import base


class Dictionary(base.BaseValue):
    def __init__(self, d) -> None:
        super().__init__(d)

    # def __repr__(self) -> str:
    #     return str(self.proxy)