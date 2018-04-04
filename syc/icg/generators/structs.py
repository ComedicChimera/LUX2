from syc.parser.ASTtools import ASTNode
from syc.icg.table import Symbol, Modifiers
import syc.icg.types as types
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
    symbol = Symbol(name, types.DataType(types.DataTypes.STRUCT, 0), modifiers, members=members)
    util.symbol_table.scope.append(symbol)


def generate_modifiers(modifier_tree):
    mods = []
    # used to map token types to enum objects
    mod_map = {
        'PROTECTED': Modifiers.PROTECTED,
        'PRIVATE': Modifiers.PRIVATE,
        'PARTIAL': Modifiers.PARTIAL,
        'EXTERN': Modifiers.EXTERNAL,
        'ABSTRACT': Modifiers.ABSTRACT
    }
    # iterate through unparsed tokens
    for item in util.unparse(modifier_tree):
        # map to enum representation
        mods.append(mod_map[item.type])
    # return
    return mods


def generate_members(member_tree):
    return member_tree
