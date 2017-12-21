from src.parser.ASTtools import Token
from src.semantics.semantics import DataType, DataTypes, ListType, DictType


str_to_enum = {
    "INT_TYPE": DataTypes.INT,
    "STRING_TYPE": DataTypes.STRING,
    "CHAR_TYPE": DataTypes.CHAR,
    "BOOL_TYPE": DataTypes.BOOL,
    "FLOAT_TYPE": DataTypes.FLOAT
}


def unparse(ast):
    unwind_list = []
    for item in ast.content:
        if isinstance(item, Token):
            unwind_list.append(item)
        else:
            unwind_list += unparse(item)
    return unwind_list


def from_simple(simple, c_type):
    if isinstance(simple.content[0], Token):
        if simple.content[0].type == "LIST_TYPE":
            c_type.data_type = ListType().element_type = from_type(simple.content[1].content[1])
        else:
            c_type.data_type = DictType().key_type = from_type(simple.content[1].content[1].content[0])
            c_type.data_type.value_type = from_type(simple.content[1].content[1].content[2])
    else:
        if simple.content[0].name == "pure_types":
            str_type = simple.content[0].content[0].type
            c_type.data_type = DataTypes(str_to_enum[str_type])
        else:
            c_type.data_type = unparse(simple.content[0])
    return c_type


def from_type(data_type):
    rt_type = DataType()
    if data_type.content[0].name == "deref_op":
        rt_type.pointer = [x.type for x in unparse(data_type[0])]
        return from_simple(data_type.content[1], rt_type)
    elif data_type.content[0].name == "simple_types":
        return from_simple(data_type.content[0], rt_type)


def from_assignment(assign):
    return assign
