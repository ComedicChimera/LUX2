import syc.icg.types as types
from syc.icg.action_tree import Literal


class Tuple:
    def __init__(self, *args):
        self.items = args
        self.count = len(args)


def create_tuple(literal):
    if isinstance(literal.data_type, types.ArrayType) or isinstance(literal.data_type, types.ListType):
        tpl = Tuple(*literal.value)
        return Literal(tpl, tpl.items)
    elif isinstance(literal.data_type, types.DictType):
        tuple_list = []
        for k, v in literal.value.items():
            tuple_list.append((k, v))
        tpl = Tuple(*tuple_list)
        return Literal(tpl, tpl.items)
    elif isinstance(literal.data_type, types.DataType):
        if literal.data_type.pointers != 0:
            return
        elif literal.data_type == types.DataTypes.STRING:
            tpl = Tuple(*literal.value.split())
            return Literal(tpl, tpl.items)
