from src.semantics import DataType
from src.ASTtools import Token


def unparse(ast):
    unwind_list = []
    for item in ast.content:
        if isinstance(item, Token):
            unwind_list.append(item)
        else:
            unwind_list += unparse(item)
    return unwind_list


def from_extension(ext):
    data_type = ext.content[1]
    rt_type = DataType()
    if data_type.content[0].name == "deref_op":
        rt_type.pointer = [x.type for x in unparse(data_type[0])]
    elif data_type.content[0].name == "simple_types":
        pass


def from_assignment(assign):
    return assign
