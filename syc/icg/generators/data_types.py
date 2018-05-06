import util
from syc.parser.ASTtools import Token
import syc.icg.types as types


# generate type from ast (extension or atom types)
def generate_type(ext):
    pointers = 0
    # handle std types (from extension)
    if ext.name == 'types':
        if ext.content[0].name == 'deref_op':
            # extract data type pointers
            pointers = len(util.unparse(ext.content[0]))
        # update ext to simple types
        ext = ext.content[-1]  # selects last element (always simple types)
    # if it is token, assume array, list or dict
    if isinstance(ext.content[0], Token):
        # assume array
        if ext.content[0].value == 'ARRAY_TYPE':
            # ext.content[1].content[1] == pure_types -> array_modifier -> types
            et = generate_type(ext.content[1].content[1])
            return types.ArrayType(et, pointers)
        # assume list
        elif ext.content[0].value == 'LIST_TYPE':
            # ext.content[1].content[1] == pure_types -> list_modifier -> types
            return types.ListType(generate_type(ext.content[1].content[1]), pointers)
        # assume function
        elif ext.content[0].value in {'FUNC', 'ASYNC'}:
            params, return_types = None, None
            for item in ext.content[1].content:
                if not isinstance(item, Token):
                    if item.name == 'func_params_decl':
                        params = generate_parameter_list(item)
                    elif item.name == 'rt_type':
                        return_types = get_return_from_type(item)
            return types.Function(params, return_types, 0, ext.content[0].value == 'ASYNC', False)
        # assume dict
        else:
            # ext.content[1].content[1] == pure_types -> dict_modifier -> types
            kt, vt = generate_type(ext.content[1].content[1]), generate_type(ext.content[1].content[3])
            # compile dictionary type
            return types.DictType(kt, vt, pointers)
    else:
        if ext.content[0].name == 'pure_types':
            # return matched pure types
            return types.DataType({
                'INT_TYPE': types.DataTypes.INT,
                'BOOL_TYPE': types.DataTypes.BOOL,
                'BYTE_TYPE': types.DataTypes.BYTE,
                'FLOAT_TYPE': types.DataTypes.FLOAT,
                'LONG_TYPE': types.DataTypes.LONG,
                'COMPLEX_TYPE': types.DataTypes.COMPLEX,
                'STRING_TYPE': types.DataTypes.STRING,
                'CHAR_TYPE': types.DataTypes.CHAR,
                'OBJECT_TYPE': types.DataTypes.OBJECT,
                'PACKAGE_TYPE': types.DataTypes.PACKAGE
                            }[ext.content[0].content[0].type], pointers)
        else:
            # TODO add get member symbol checking
            # invalid code ->
            """sym = util.symbol_table.look_up(ext.content[0].value)
            if not sym:
                errormodule.throw('semantic_error', 'Variable \'%s\' is undefined' % ext.content[0].value, ext.content[0])
            return types.CustomType(sym.data_type, sym, sym.inherits if hasattr(sym, 'inherits') else [])"""

from syc.icg.generators.functions import generate_parameter_list, get_return_from_type
