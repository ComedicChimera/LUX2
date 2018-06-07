from syc.ast.ast import Token, unparse
import errormodule
import util

from syc.icg.constexpr import get_array_bound
import syc.icg.modules as modules
import syc.icg.types as types


# generate type from ast (extension or atom types)
def generate_type(ext):
    pointers = 0
    # handle std types (from extension)
    if ext.name == 'types':
        if ext.content[0].name == 'deref_op':
            # extract data type pointers
            pointers = len(unparse(ext.content[0]))
        # update ext to simple types
        ext = ext.content[-1]  # selects last element (always simple types)
    # if it is token, assume array, list or dict
    if isinstance(ext.content[0], Token):
        # assume array
        if ext.content[0].type == 'ARRAY_TYPE':
            # ext.content[1].content[1] == pure_types -> array_modifier -> types
            et = generate_type(ext.content[1].content[1])
            # extract count value
            # ext.content[1].content[1] == pure_types -> array_modifiers -> expr
            error_ast = ext.content[1].content[3]
            try:
                count = get_array_bound(generate_expr(ext.content[1].content[3]))
            except IndexError:
                errormodule.throw('semantic_error', 'Index out of range', error_ast)
                return
            print(count)
            if not count and count != 0:
                errormodule.throw('semantic_error', 'Non-constexpr array bound', error_ast)
            elif type(count) == bool:
                errormodule.throw('semantic_error', 'Invalid value for array bound', error_ast)
            try:
                _ = count < 0
                count = float(count)
            except (ValueError, TypeError):
                errormodule.throw('semantic_error', 'Invalid value for array bound', error_ast)
            if not count.is_integer():
                errormodule.throw('semantic_error', 'Invalid value for array bound', error_ast)
            elif count < 1:
                errormodule.throw('semantic_error', 'Invalid value for array bound', error_ast)
            return types.ArrayType(et, int(count), pointers)
        # assume list
        elif ext.content[0].type == 'LIST_TYPE':
            # ext.content[1].content[1] == pure_types -> list_modifier -> types
            return types.ListType(generate_type(ext.content[1].content[1]), pointers)
        # assume function
        elif ext.content[0].type in {'FUNC', 'ASYNC'}:
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
            # check mutability
            if types.mutable(kt):
                errormodule.throw('semantic_error', 'Invalid key type for dictionary', ext.content[1].content[1])
            # compile dictionary type
            return types.MapType(kt, vt, pointers)
    else:
        if ext.content[0].name == 'pure_types':
            # data type literal
            if ext.content[0].content[0].type == 'DATA_TYPE':
                return types.DataTypeLiteral(types.DataTypes.DATA_TYPE)
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
                'OBJECT_TYPE': types.OBJECT_TEMPLATE,
                            }[ext.content[0].content[0].type], 0)
        else:
            # get root symbol
            name = ext.content[0].content[0].value
            if name.type == 'THIS':
                sym = modules.get_instance()
            else:
                sym = util.symbol_table.look_up(name)
            # hold previous symbol ASTNode for error messages
            prev_sym = ext.content[0].content[0]
            # extract outer symbols if necessary
            if len(ext.content[0].content) > 1:
                content = ext.content[0].content[1:]
                for item in content:
                    if isinstance(item, Token):
                        if item.type == 'IDENTIFIER':
                            # make sure symbol is a custom type
                            if not isinstance(sym, types.CustomType):
                                errormodule.throw('semantic_error', 'Object is not a valid is a data type', prev_sym)
                            identifier = item.value
                            # get member for modules
                            if sym.data_type.data_type == types.DataTypes.MODULE:
                                # get and check property
                                prop = modules.get_property(sym.data_type, identifier)
                                if not prop:
                                    errormodule.throw('semantic_error', 'Object has no member \'%s\'' % identifier, item)
                                # update previous symbol
                                prev_sym = item
                                # update symbol
                                sym = prop
                            # invalid get member on interfaces
                            elif sym.data_type.data_type == types.DataTypes.INTERFACE:
                                errormodule.throw('semantic_error', '\'.\' is not valid for this object', item)
                            # assume struct or enum
                            else:
                                for member in sym.data_type.members:
                                    # if there is a match, extract value
                                    if member.name == identifier:
                                        prev_sym = item
                                        sym = member
                                        # break to prevent else condition
                                        break
                                # if there is no match, throw error
                                else:
                                    errormodule.throw('semantic_error', 'Object has no member \'%s\'' % identifier, item)
                    # continue recursive for loop
                    elif item.name == 'dot_id':
                            content.extend(item.content)
            # final check for invalid data types
            if not isinstance(sym, types.CustomType):
                errormodule.throw('semantic_error', 'Object is not a valid is a data type', prev_sym)
            # add instance marker if necessary
            if sym.data_type.data_type != types.DataTypes.INTERFACE:
                sym.data_type.instance = True
            return sym.data_type


from syc.icg.generators.functions import generate_parameter_list, get_return_from_type
from syc.icg.generators.expr import generate_expr
