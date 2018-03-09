from src.parser.ASTtools import Token
import src.semantics.types as types


# converts an ast to a list of its elements
def unparse(ast):
    unwind_list = []
    for item in ast.content:
        if isinstance(item, Token):
            unwind_list.append(item)
        else:
            unwind_list += unparse(item)
    return unwind_list


# removes periods from a group declaration (returns a list of named elements)
def remove_periods(group):
    group = [group.content[0]] + unparse(group.content[1])
    n_group = []
    x = 0
    for item in group:
        if x % 2 == 0:
            n_group.append(item)
        x += 1
    n_group.pop()
    return [x.value for x in n_group]


# creates an identifier list for a given set of elements
def compile_identifier(id):
    if len(id.content) < 2:
        if id.content[0].type == "THIS":
            return ["", [], True]
        return [id.content[0].value, [], False]
    else:
        if id.content[0].type == "THIS":
            return [unparse(id)[-1].value, remove_periods(id), True]
        return [unparse(id)[-1].value, remove_periods(id), False]


# generates from a simple data type
def from_simple(simple, r_depth):
    simple_types = {
        'LONG_TYPE': types.Long,
        'INT_TYPE': types.Integer,
        'FLOAT_TYPE': types.Float,
        'COMPLEX_TYPE': types.Complex,
        'CHAR_TYPE': types.Char,
        'STRING_TYPE': types.String,
        'BOOL_TYPE': types.Boolean
    }
    if isinstance(simple.content[0], Token):
        if simple.content[0].type == "LIST_TYPE":
            f_type = types.List(from_type(simple.content[1].content[1]))
            f_type.reference_depth = r_depth
            return f_type
        else:
            f_type = types.Dictionary(from_type(simple.content[1].content[1].content[0]), from_type(simple.content[1].content[1].content[2]))
            f_type.reference_depth = r_depth
            return f_type
    else:
        if simple.content[0].name == "pure_types":
            f_type = simple_types[simple.content[0].content[0].type]()
            f_type.reference_depth = r_depth
            return f_type
        else:
            return "".join(unparse(simple.content[0]))


# generates from a type declaration (types in grammar)
def from_type(data_type):
    # handles dereference operators
    if data_type.content[0].name == "deref_op":
        rt_type = len(data_type.content[0])
        return from_simple(data_type.content[1], rt_type)
    elif data_type.content[0].name == "simple_types":
        return from_simple(data_type.content[0], 0)
