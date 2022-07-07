from values import base, float
import operator

def foobar(a, b, op):
    value = op(a._val, b._val)
    if isinstance(a, float.Float) or isinstance(b, float.Float):
        return float.Float(value)
    else:
        return Integer(value)


class Integer(base.BaseValue):
    def __init__(self, val) -> None:
        self._val = val

    def __add__(self, other):
        return foobar(self, other, operator.add)
    def __sub__(self, other):
        return foobar(self, other, operator.sub)
    def __mul__(self, other):
        return foobar(self, other, operator.mul)
    def __div__(self, other):
        return foobar(self, other, operator.div)

    def __lt__(self, other):
        return self._val < other._val

    def __repr__(self) -> str:
        return str(self._val)