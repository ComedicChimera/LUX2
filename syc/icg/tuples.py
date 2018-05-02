import syc.icg.types as types


class Tuple:
    def __init__(self, *args):
        self.items = args
        self.count = len(args)


def create_tuple(literal):
    if isinstance(literal.data_type, types.ArrayType) or isinstance(literal.data_type, types.ListType):
        return Tuple(*literal.value)
    elif isinstance(literal.data_type, types.DictType):
        tuple_list = []
        for k, v in literal.value.items():
            tuple_list.append((k, v))
        return Tuple(*tuple_list)
    elif isinstance(literal.data_type, types.DataType):
        if literal.data_type.pointers != 0:
            return
        elif literal.data_type == types.DataTypes.STRING:
            return Tuple(*literal.value.split())
