from syc.ast.ast import ASTNode, unparse
from syc.icg.table import Symbol, Modifiers
import syc.icg.types as types
from syc.icg.generators.data_types import generate_type
import syc.icg.modules as modules
import util


def generate_struct(struct_tree):
    # hold modifiers
    modifiers = []
    # hold name of symbol
    name = ''
    # hold generate members
    members = []
    # extract elements from AST
    for item in struct_tree:
        if isinstance(item, ASTNode):
            if item.name == 'modifiers':
                modifiers = generate_modifiers(item)
            elif item.name == 'struct_main':
                members = generate_members(item)
        else:
            if item.type == 'IDENTIFIER':
                name = item.value
    # generate symbol
    symbol = Symbol(name, types.CustomType(name, types.DataTypes.STRUCT, members, []), modifiers)
    util.symbol_table.scope.append(symbol)


def generate_modifiers(modifier_tree):
    mods = []
    # used to map token types to enum objects
    mod_map = {
        'PROTECTED': Modifiers.PROTECTED,
        'PRIVATE': Modifiers.PRIVATE,
        'PARTIAL': Modifiers.PARTIAL,
        'EXTERN': Modifiers.EXTERNAL,
        'ABSTRACT': Modifiers.ABSTRACT,
        'STATIC': Modifiers.STATIC,
        'FINAL': Modifiers.FINAL,
        'VOLATILE': Modifiers.VOLATILE,
        'SEALED': Modifiers.SEALED
    }
    # iterate through unparsed tokens
    for item in unparse(modifier_tree):
        # map to enum representation
        mods.append(mod_map[item.type])
    # check modifiers
    modules.check_modifiers(mods)
    # return
    return mods


def generate_members(member_tree):
    members = []
    working_member = {}
    for item in member_tree.content:
        if isinstance(item, ASTNode):
            if item.name == 'n_var':
                members += generate_members(item)
            elif item.name == 'extension':
                working_member['data_type'] = generate_type(item.content[1])
        elif item.type == 'IDENTIFIER':
            working_member['name'] = item.value
    if 'data_type' not in working_member.keys():
        working_member['data_type'] = types.DataType(types.DataTypes.OBJECT, 0)
    members.append(type('Object', (), working_member))
    return members


def check_constructor(struct, params):
    pass
