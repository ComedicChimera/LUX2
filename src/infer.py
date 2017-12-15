from src.semantics import DataType
from src.ASTtools import Token


def unwind(ast):
    unwind_list = []
    for item in ast.content:
        if isinstance(item, Token):
            unwind_list.append(unwind_list)
        else:
            unwind_list += unwind(item)
    return unwind_list


def from_extension(ext):
    data_type = ext.content[1]
    rt_type = DataType()
    if data_type[0].name == "deref_op":
        rt_type.pointer = [x.type for x in unwind(data_type[0])]
    elif data_type[0].name == "simple_types":
        pass


def from_assignment(assign):
    return assign
