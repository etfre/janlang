import operator


def create_type_maps():
    import values

    m1 = {
        bool: values.Boolean,
        int: values.Integer,
        float: values.Float,
        list: values.List,
        dict: values.Dictionary,
    }
    m2 = {v: k for k, v in m1.items()}
    return m1, m2


map_python_to_jan_types = None
map_jan_to_python_types = None


class NoProxy:
    pass


class BaseValue:
    def __init__(self, proxy=NoProxy) -> None:
        global map_python_to_jan_types
        global map_jan_to_python_types
        if not isinstance(proxy, NoProxy):
            if map_jan_to_python_types is None:
                map_python_to_jan_types, map_jan_to_python_types = create_type_maps()
                assert map_python_to_jan_types[type(proxy)] is type(self)
        self.proxy = proxy

    def __add__(self, other):
        return binary_op(self, other, operator.add)

    def __sub__(self, other):
        return binary_op(self, other, operator.sub)

    def __mul__(self, other):
        return binary_op(self, other, operator.mul)

    def __div__(self, other):
        return binary_op(self, other, operator.div)

    def __eq__(self, other):
        return binary_op(self, other, operator.eq)

    def __ne__(self, other):
        return binary_op(self, other, operator.ne)

    def __lt__(self, other):
        return binary_op(self, other, operator.lt)

    def __le__(self, other):
        return binary_op(self, other, operator.le)

    def __gt__(self, other):
        return binary_op(self, other, operator.gt)

    def __ge__(self, other):
        return binary_op(self, other, operator.ge)

    def __getitem__(self, i):
        obj = self.proxy[get_python_obj(i)]
        return obj

    def __bool__(self):
        if not isinstance(self.proxy, NoProxy):
            py_bool = bool(get_python_obj(self))
            return py_bool
        raise NotImplementedError

    def __iter__(self):
        if not isinstance(self.proxy, NoProxy):
            return iter(self.proxy)
        raise NotImplementedError


def get_python_obj(value: BaseValue):
    """python object from jan value"""
    assert type(value.proxy) in map_python_to_jan_types
    return value.proxy


def jan_object_from_python(py_obj):
    return map_python_to_jan_types[type(py_obj)](py_obj)


def binary_op(obj: BaseValue, other, op):
    if not isinstance(obj.proxy, NoProxy):
        left = get_python_obj(obj)
        right = get_python_obj(other)
        result = op(left, right)
        return jan_object_from_python(result)
    raise NotImplementedError
