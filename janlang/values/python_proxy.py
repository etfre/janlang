# class PythonProxyObj:
#     def __init__(self, obj):
#         import values
#         self.obj = obj
#         self.unwrap_type = {
#             values.Boolean: bool,
#             values.Integer: int,
#             values.Float: float,
#             values.List: list,
#         }[type(obj)]

#     def unwrap(self):
#         return self.unwrap_type(self.obj)




# def wrap(obj: any):
#     import values

#     value_type = {
#         bool: values.Boolean,
#         int: values.Integer,
#         float: values.Float,
#         list: values.List,
#     }[type(obj)]
#     return value_type(obj)
