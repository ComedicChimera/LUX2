import errormodule
import syc.icg.modules as modules
from syc.icg.table import Symbol, Modifiers, Package
from syc.ast.ast import ASTNode, Token
import util
from syc.icg.action_tree import ExprNode, Identifier, Literal
import syc.icg.types as types
import syc.icg.generators.functions as functions
from syc.icg.generators.data_types import generate_type
from copy import copy


#########
# ATOMS #
#########


def generate_atom(atom):
    # the only component of the atom grammar that begins with token is ( expr ) trailer
    if isinstance(atom.content[0], Token):
        # generate root tree
        expr_tree = generate_expr(atom.content[1])

        # apply distribution operator
        if len(atom.content) > 3:
            if atom.content[3].name == 'distribute':
                distribute_expr = generate_expr(atom.content[3].content[1])
                if not isinstance(distribute_expr.data_type, types.Function):
                    if isinstance(distribute_expr.data_type, types.CustomType) and distribute_expr.data_type.callable:
                        method = modules.get_property(distribute_expr.data_type, '__call__')
                        expr_tree = ExprNode('Distribute', method.data_type.return_type, expr_tree, ExprNode('Call', method.data_type.return_type, method))
                else:
                    expr_tree = ExprNode('Distribute', distribute_expr.data_type.return_type, expr_tree, distribute_expr)
            # type check expr tree
            if isinstance(expr_tree.data_type, types.DataType):
                if expr_tree.data_type.pointers != 0:
                    errormodule.throw('semantic_error', 'Unable to apply distribution to operator to pointer', atom)
                elif not expr_tree.data_type.data_type != types.DataTypes.TUPLE and not expr_tree.data_type.data_type != types.DataTypes.STRING:
                    errormodule.throw('semantic_error', 'Invalid data type from distribution operator', atom)
            elif isinstance(expr_tree.data_type, types.CustomType) and not expr_tree.data_type.enumerable:
                errormodule.throw('semantic_error', 'Module used for distribution is not enumerable', atom)
        # if it has a trailer, add to expr root tree
        if isinstance(atom.content[-1], ASTNode) and atom.content[-1].name == 'trailer':
            expr_tree = add_trailer(expr_tree, atom.content[-1])
        return expr_tree
    else:
        # all other elements are ASTNodes
        # if the first element is lambda (as in 'lambda trailer')
        if atom.content[0].name == 'inline_for':
            lb = generate_comprehension(atom.content[0])
            # if there is extra content, assume trailer and add to lambda root
            if len(atom.content) > 1:
                lb = add_trailer(lb, atom.content[-1])
            # return compiled lambda
            return lb
        else:
            # constants to hold whether of not base is awaited or dynamic allocation is called on it
            await, new, base, = False, False, None
            # iterate through atom collect components
            for item in atom.content:
                # set await to true if element is awaited
                await = True if item.name == 'await' else await
                # set new to true if object is dynamically allocated / object
                new = True if item.name == 'new' else new
                # create base from atom parts
                # add trailer to base
                if item.name == 'trailer':
                    base = add_trailer(base, item)
                    break
                # otherwise compile base
                base = generate_base(item) if item.name == 'base' else None
            # if awaited and not an async function, throw an error
            if await and not isinstance(base.data_type, types.Future):
                errormodule.throw('semantic_error', 'Unable to await object', atom)
            elif await:
                base = ExprNode('Await', base.data_type.data_type, base)
            # if instance type is a custom Type or normal data type
            if new and isinstance(base.data_type, types.CustomType) | isinstance(base.data_type, types.DataType):
                # if it is not a structure of a group
                if base.data_type not in [types.DataType(types.DataTypes.STRUCT, 0), types.DataType(types.DataTypes.MODULE, 0)]:
                    # if it is a data type
                    if isinstance(base.data_type, types.DataTypeLiteral):
                        # get new pointer type
                        dt = copy(base.data_type)
                        dt.pointers += 1
                        # return memory allocation with size of type
                        base = ExprNode('Malloc', dt, ExprNode('SizeOf', types.DataType(types.DataTypes.INT, 1), base))
                    else:
                        # if it is not an integer
                        if base.data_type != types.DataType(types.DataTypes.INT, 0):
                            # all tests failed, not allocatable
                            errormodule.throw('semantic_error', 'Unable to dynamically allocate memory for object', atom)
                        else:
                            # malloc for just int size
                            base = ExprNode('Malloc', types.VOID_PTR, base)

                else:
                    # return object instance
                    dt = copy(base.data_type)
                    dt.instance = True
                    base = ExprNode('CreateObjectInstance', dt, base)
            elif new:
                # throw error if list, instance, or dict
                errormodule.throw('semantic_error', 'Unable to dynamically allocate memory for object', atom)
            return base


# move import below to allow for recursive imports
from syc.icg.generators.expr import generate_expr
import syc.icg.generators.structs as structs
import syc.icg.casting as casting


############
# TRAILERS #
############


def add_trailer(root, trailer):
    # root with trailer added
    trailer_added = None
    # assume first is token
    # if is function call
    if trailer.content[0].type == '(':
        trailer_added = add_call_trailer(root, trailer)
    # if is subscript
    elif trailer.content[0].type == '[':
        trailer_added = add_subscript_trailer(root, trailer)
    # if it is a get member
    elif trailer.content[0].type == '.':
        trailer_added = add_get_member_trailer(root, trailer)
    # handle distribute
    elif trailer.content[0].type == '|>':
        trailer_added = add_aggregator_trailer(root, trailer)
    # continue adding trailer
    if isinstance(trailer.content[-1], ASTNode):
        if trailer.content[-1].name == 'trailer':
            return add_trailer(trailer_added, trailer.content[-1])
    # otherwise return completed item
    return trailer_added


# add function call '()' trailer
def add_call_trailer(root, trailer):
    # if it is a function
    if isinstance(root.data_type, types.Function):
        # handle invalid calls on function pointers
        if root.data_type.pointers != 0:
            errormodule.throw('semantic_error', 'Function pointers are not callable', trailer)
        else:
            parameters = functions.compile_parameters(trailer.content[1])
            functions.check_parameters(root, parameters, trailer)
            return ExprNode('Call', types.Future(root.data_type) if root.data_type.async else root.data_type.return_type,
                            root, parameters)
    elif isinstance(root.data_type, types.DataType):
        if root.data_type.pointers == 0:
            # call (struct) constructor
            if root.data_type.data_type == types.DataTypes.STRUCT:
                # check struct generator
                parameters = structs.check_constructor(root.data_type, trailer.content[1])
                return ExprNode('Constructor', root.data_type, root, parameters)
            elif root.data_type.data_type == types.DataTypes.VALUE:
                return casting.value_cast(generate_expr(trailer.content[1]))
        errormodule.throw('semantic_error', 'Unable to call non-callable type', trailer)
    # if is module
    elif isinstance(root.data_type, types.CustomType):
        if root.pointers != 0:
            errormodule.throw('semantic_error', 'Unable to call non-callable type', trailer)
        else:
            constructor = modules.get_constructor(root.data_type.members)
            parameters = modules.check_constructor_parameters(constructor, trailer.content[1])
            return ExprNode('Call', root.data_type, constructor, parameters)
    # type cast
    elif isinstance(root.data_type, types.DataTypeLiteral):
        # 'type' cannot be cast to
        if root.data_type.data_type.data_type == types.DataTypes.DATA_TYPE:
            errormodule.throw('semantic_error', 'Invalid type cast', trailer)
        # handle null type casts
        if isinstance(trailer.content[1], Token):
            errormodule.throw('semantic_error', 'Type cast must be performed on at least one object', trailer)
        # get parameters of type cast
        parameters = trailer.content[1].content
        # ensure parameters are valid
        if len(parameters) > 1:
            # no named parameters
            if parameters[1].name == 'named_params':
                errormodule.throw('semantic_error', 'Type cast does not accept named parameters',
                                  trailer.content[1])
            # too many parameters for type cast
            else:
                errormodule.throw('semantic_error', 'Unable to perform type cast on multiple objects',
                                  trailer.content[1])
        # generate casting object
        obj = generate_expr(parameters[0])
        # static cast if literal
        if isinstance(obj, Literal):
            tp = root.data_type.data_type
            if not casting.static_cast(tp, obj):
                errormodule.throw('semantic_error', 'Invalid type cast', trailer)
            # check for interface type cast (assume obj is custom type)
            if isinstance(tp, types.CustomType) and tp.data_type == types.DataTypes.INTERFACE and obj.data_type.data_type != tp.data_type:
                ndt = copy(obj.data_type)
                ndt.interfaces.append(tp.name)
                ndt.update_interface_overloads()
                return ExprNode('TypeCast', ndt, root, obj)
            return ExprNode('TypeCast', tp, root, obj)
        # use raw type based cast
        else:
            # if dynamic cast fails
            if not casting.dynamic_cast(root.data_type.data_type, obj.data_type):
                errormodule.throw('semantic_error', 'Invalid type cast', trailer)
            else:
                # check for interface type cast (assume obj is custom type)
                if isinstance(root.data_type, types.CustomType) and root.data_type.data_type == types.DataTypes.INTERFACE and \
                                obj.data_type.data_type != root.data_type.data_type:
                    ndt = copy(obj.data_type)
                    ndt.interfaces.append(root.data_type.name)
                    ndt.update_interface_overloads()
                    return ExprNode('TypeCast', ndt, root, obj)
                return ExprNode('TypeCast', root.data_type, root, obj)
    # throw invalid call error
    else:
        errormodule.throw('semantic_error', 'Unable to call non-callable type', trailer)


# add subscript/slice '[]' trailer
def add_subscript_trailer(root, trailer):
    # handle slicing
    if isinstance(trailer.content[1].content[0], Token):
        expr = generate_expr(trailer.content[1].content[1])
        # subscript cannot be a pointer
        if expr.data_type.pointers != 0:
            errormodule.throw('semantic_error', 'Subscript cannot be a pointer', trailer)
        # check begin subscript
        # check for invalid data types
        if not isinstance(expr.data_type, types.DataType):
            errormodule.throw('semantic_error', 'Invalid slice parameter', trailer)
        if expr.data_type.data_type == types.DataTypes.INT and (isinstance(root.data_type, types.ListType) or isinstance(root.data_type, types.ArrayType)):
            return ExprNode('SliceBegin', root.data_type, root, expr)
        # overload based slicing
        elif isinstance(root.data_type, types.CustomType):
            method = modules.get_property(root.data_type, '__slice__')
            if method:
                functions.check_parameters(method, [expr], trailer)
                return ExprNode('Call', method.data_type.return_type, method, expr)
            errormodule.throw('semantic_error', 'Object has no method \'__slice__\'', trailer)
        # string slicing
        elif root.data_type.data_type == types.DataTypes.STRING and expr.data_type.data_type == types.DataTypes.INT:
            return ExprNode('SliceBegin', root.data_type, root, expr)
        # check for invalid integer slicing
        if not isinstance(expr.data_type, types.DataType) or expr.data_type.data_type != types.DataTypes.INT:
            errormodule.throw('semantic_error', 'Index must be an integral value', trailer)
        errormodule.throw('semantic_error', 'Unable to perform slice on non slice-able object', trailer)
    # handle slice till end / general slice
    elif len(trailer.content[1].content) > 1:
        # first expression of slice
        expr = generate_expr(trailer.content[1].content[0])
        # check for invalid pointers
        if expr.data_type.pointers > 0:
            errormodule.throw('semantic_error', 'Invalid slice parameter', trailer)
        # check for invalid slice data type
        if not isinstance(expr.data_type, types.DataType):
            errormodule.throw('semantic_error', 'Invalid slice parameter', trailer)
        if expr.data_type.data_type != types.DataTypes.INT:
            errormodule.throw('semantic_error', 'Invalid slice parameter', trailer)
        # check for two way slicing
        if len(trailer.content[1].content[1].content) > 1:
            # get secondary expression
            expr2 = generate_expr(trailer.content[1].content[1].content[1].content[0])
            # check secondary expression
            # no pointers
            if expr2.data_type.pointers > 0:
                errormodule.throw('semantic_error', 'Invalid slice parameter', trailer)
            # check for invalid data types
            if not isinstance(expr2.data_type, types.DataType):
                errormodule.throw('semantic_error', 'Invalid slice parameter', trailer)
            # ensure correct data type
            if expr2.data_type.data_type != types.DataTypes.INT:
                errormodule.throw('semantic_error', 'Invalid slice parameter', trailer)
            if not isinstance(root.data_type, types.ListType) and not isinstance(root.data_type, types.ArrayType):
                # operator overloading
                if isinstance(root.data_type, types.CustomType):
                    slice_method = modules.get_property(root.data_type, '__slice__')
                    if slice_method:
                        functions.check_parameters(slice_method, [expr, expr2], trailer)
                        return ExprNode('Call', slice_method.data_type.return_type, slice_method, expr, expr2)
                # string slicing
                elif isinstance(root.data_type, types.DataType) and root.data_type.data_type == types.DataTypes.STRING:
                    return ExprNode('Slice', types.DataType(types.DataTypes.CHAR, 0), root, expr, expr2)
                errormodule.throw('semantic_error', 'Unable to perform slice on non slice-able object', trailer)
            return ExprNode('Slice', root.data_type, root, expr, expr2)
        # check slice till end
        else:
            if not isinstance(root.data_type, types.ListType) and not isinstance(root.data_type, types.ArrayType):
                # use operator overloading
                if isinstance(root.data_type, types.CustomType):
                    slice_method = modules.get_property(root.data_type, '__slice__')
                    if slice_method:
                        functions.check_parameters(slice_method, [None, expr], trailer)
                        return ExprNode('Call', slice_method.data_type.return_type, slice_method, None, expr)
                # use string overloading
                elif isinstance(root.data_type, types.DataType) and root.data_type.data_type == types.DataTypes.STRING:
                    return ExprNode('SliceEnd', root.data_type, root, expr)
                errormodule.throw('semantic_error', 'Unable to perform slice on non slice-able object', trailer)
            # general slice
            return ExprNode('SliceEnd', root.data_type, root, expr)
    # handle traditional subscripting
    else:
        # the only subscriptable components are mutable (except for strings)
        if types.mutable(root.data_type):
            expr = generate_expr(trailer.content[1].content[0])
            # if not dict, use element type, not value type
            if isinstance(root.data_type, types.DictType):
                if expr.data_type != root.data_type.key_type and not types.coerce(root.data_type.key_type, expr.data_type):
                    errormodule.throw('semantic_error',
                                      'Type of subscript on dictionary must match data type of dictionary', trailer)
                dt = root.data_type.value_type
            elif isinstance(expr.data_type, types.DataType) and expr.data_type.data_type == types.DataTypes.INT:
                dt = root.data_type.element_type
            else:
                errormodule.throw('semantic_error', 'Invalid type for subscript', trailer)
                dt = None
            return ExprNode('Subscript', dt, expr, root)
        # if it is a module
        elif isinstance(root.data_type, types.CustomType) and root.data_type.data_type == types.DataType(types.DataTypes.MODULE, 0):
            # if it has subscript method
            subscript_method = modules.get_property(root.data_type, '__subscript__')
            if subscript_method:
                expr = generate_expr(trailer.content[1].content[0])
                functions.check_parameters(subscript_method, [expr], trailer)
                return ExprNode('Call', subscript_method.data_type.return_type, subscript_method, expr)
            # otherwise it is invalid
            else:
                errormodule.throw('semantic_error', 'Object has no method \'__subscript__\'', trailer)
        # strings members can be subscripted, but they cannot modified
        elif root.data_type == types.DataType(types.DataTypes.STRING, 0):
            expr = generate_expr(trailer.content[1])
            if isinstance(expr.data_type, types.DataType) and expr.data_type.data_type == types.DataTypes.INT:
                return ExprNode('Subscript', types.DataType(types.DataTypes.CHAR, 0), expr, root)
            else:
                errormodule.throw('semantic_error', 'Strings can only be subscripted using integers', trailer)
        else:
            errormodule.throw('semantic_error', 'Object is not subscriptable', trailer)


# add get member '.' trailer
def add_get_member_trailer(root, trailer):
    # if it is a custom type
    if isinstance(root.data_type, types.CustomType):
        # interface members cannot be accessed
        if root.data_type.data_type == types.DataTypes.INTERFACE:
            errormodule.throw('semantic_error', '\'.\' is not valid for this object', trailer.content[0])
        # use module method if necessary
        elif root.data_type.data_type == types.DataTypes.MODULE:
            prop = modules.get_property(root.data_type, trailer.content[1].value)
            if prop:
                return ExprNode('GetMember', prop.data_type, root, Identifier(prop.name, prop.data_type, Modifiers.CONSTANT in prop.modifiers, Modifiers.CONSTEXPR in prop.modifiers))
            errormodule.throw('semantic_error', 'Object has no member \'%s\'' % trailer.content[1].value, trailer.content[1])
        # assume struct or enum
        else:
            # check to ensure it is an instance of a struct if it is a struct
            if root.data_type.data_type == types.DataTypes.STRUCT:
                if not root.data_type.instance:
                    errormodule.throw('semantic_error', '\'.\' is not valid for this object', trailer.content[0])
            identifier = trailer.content[1].value
            member_names = [x.name for x in root.data_type.members if x.name == identifier]
            if identifier in member_names:
                member = [x for x in root.data_type.members if x.name == identifier][0]
                # convert member data type for enums
                if root.data_type.data_type == types.DataTypes.ENUM:
                    # copy enum data type
                    enum_dt = copy(root.data_type)
                    # set instance
                    enum_dt.instance = True
                    # add the value property to it
                    setattr(enum_dt, 'value', Identifier(member.name, member.data_type, True, Modifiers.CONSTEXPR in member.modifiers))
                    # return generated expression node
                    return ExprNode('GetMember', enum_dt, root, Identifier(member.name, member.data_type, True, Modifiers.CONSTEXPR in member.modifiers))
                # return struct get member
                return ExprNode('GetMember', member.data_type, root, Identifier(member.name, member.data_type, Modifiers.CONSTANT in member.modifiers,
                                                                                Modifiers.CONSTEXPR in member.modifiers))
            errormodule.throw('semantic_error', 'Object has no member \'%s\'' % identifier, trailer.content[1])
    # if it is a package
    elif isinstance(root, Package):
        prop = root.get_member(trailer.content[1].value)
        if prop:
            return ExprNode('GetMember', prop.data_type, root, prop)
        errormodule.throw('semantic_error', 'Package has no member \'%s\'' % trailer.content[1].value, trailer.content[1])
    # otherwise it is invalid
    else:
        errormodule.throw('semantic_error', '\'.\' is not valid for this object', trailer.content[0])


# add aggregator '|>' trailer
def add_aggregator_trailer(root, trailer):
    dt = None
    # type check root
    if isinstance(root.data_type, types.DataType):
        if root.data_type.pointers != 0:
            errormodule.throw('semantic_error', 'Unable to apply aggregation to operator to pointer', trailer)
        elif not root.data_type.data_type != types.DataTypes.STRING:
            errormodule.throw('semantic_error', 'Invalid data type from aggregation operator', trailer)
        dt = types.DataType(types.DataTypes.CHAR, 0)
    elif isinstance(root.data_type, types.CustomType):
        if not root.data_type.enumerable:
            errormodule.throw('semantic_error', 'Module used for aggregation is not enumerable', trailer)
        dt = modules.get_property(root.data_type, '__next__').data_type.return_type
    elif isinstance(root.data_type, types.ListType) or isinstance(root.data_type, types.ArrayType):
        dt = root.data_type.element_type
    elif isinstance(root.data_type, types.DictType):
        dt = (root.data_type.key_type, root.data_type.value_type)
    # check the aggregator expr
    aggregate_expr = generate_expr(trailer.content[1])
    # if it isn't a function
    if not isinstance(aggregate_expr.data_type, types.Function):
        errormodule.throw('semantic_error', 'Aggregator must be a function', trailer.content[1])
    # otherwise add
    else:
        # check parameters
        if len(aggregate_expr.data_type.parameters) != 2:
            errormodule.throw('semantic_error', 'Aggregator can only take two parameters', trailer.content[1])
        # check dictionary
        if isinstance(dt, tuple):
            params = aggregate_expr.data_type.parameters
            if not types.coerce(params[0].data_type, dt[0]) or not types.coerce(params[1].data_type, dt[1]):
                errormodule.throw('semantic_error', 'Aggregator function parameters must match the key and value types of the dictionary', trailer.content[1])
        # check all others
        else:
            if any(not types.coerce(x.data_type, dt) for x in aggregate_expr.data_type.parameters):
                errormodule.throw('semantic_error', 'Aggregator function parameters must match the element type of the aggregate set', trailer.content[1])
        return ExprNode('Aggregate', aggregate_expr.data_type.return_type, root, aggregate_expr)


#########
# BASES #
#########

# generate a base from a base AST
def generate_base(ast):
    # get that actual base from the ast
    base = ast.content[0]
    # check if base is token
    if isinstance(base, Token):
        # if it is an identifier
        if base.type == 'IDENTIFIER':
            # look it up in the s-table
            sym = util.symbol_table.look_up(base.value)
            # if it is not able to found in the table, throw an error
            if not sym:
                errormodule.throw('semantic_error', 'Variable used without declaration', ast)
            # otherwise return the Identifier
            return Identifier(sym.name, sym.data_type, Modifiers.CONSTANT in sym.modifiers, Modifiers.CONSTEXPR in sym.modifiers)
        # if it is an instance pointer
        elif base.type == 'THIS':
            # get the group instance (typeof Instance)
            module_instance = modules.get_instance()
            # if there is not current group instance
            if not module_instance:
                errormodule.throw('semantic_error', 'This used outside of instance group', ast)
            # else return group instance
            return module_instance
        # if null, return null literal
        elif base.type == 'NULL':
            return Literal(types.DataType(types.DataTypes.NULL, 0), None)
        # if base is a bool literal
        elif base.type == 'BOOL_LITERAL':
            return Literal(types.DataType(types.DataTypes.BOOL, 0), base.value.lower())
        # if base is value, return value
        else:
            return Literal(types.DataType(types.DataTypes.VALUE, 0), 'value')
    else:
        # if the base is character-like object
        if base.name == 'string':
            # if it is a char, return a char literal
            if base.content[0].type == 'CHAR_LITERAL':
                return Literal(types.DataType(types.DataTypes.CHAR, 0), base.content[0].value)
            # otherwise return a string literal
            else:
                return Literal(types.DataType(types.DataTypes.STRING, 0), base.content[0].value)
        # if the base is numeric
        if base.name == 'number':
            # if it is a float
            if base.content[0].type == 'FLOAT_LITERAL':
                return Literal(types.DataType(types.DataTypes.FLOAT, 0), base.content[0].value)
            # if it is a complex
            elif base.content[0].type == 'COMPLEX_LITERAL':
                return Literal(types.DataType(types.DataTypes.COMPLEX, 0), base.content[0].value)
            # if it is an integer or long
            else:
                # if the integer's value is greater than the maximum value accepted by an int32
                # it is taken as a long literal
                if int(base.content[0].value) > 2147483647:
                    return Literal(types.DataType(types.DataTypes.LONG, 0), base.content[0].value)
                # otherwise, it is taken as an integer literal (int32)
                else:
                    return Literal(types.DataType(types.DataTypes.INT, 0), base.content[0].value)
        # if it is a list literal
        elif base.name == 'list':
            # generate a list from the base tree
            return generate_list(base)
        # check if data is byte
        elif base.name == 'byte':
            # extract the core literal value
            val = base.content[0].value
            # check if binary or hexadecimal
            if val.startswith('0b'):
                # if it has more than 8 binary digits (10 because prefix)
                # MAX 0b11111111
                if len(val) > 10:
                    # generate byte array (ALL BYTE ARRAYS MADE UP OF HEX LITERALS)
                    return generate_byte_array(val)
                else:
                    # return raw byte literal (converted to hex literal)
                    return Literal(types.DataType(types.DataTypes.BYTE, 0), hex(int(val[2:])))
            else:
                # if it has more than 2 digits (4 because prefix)
                # MAX 0xFF
                if len(val) > 4:
                    # generate a normal byte array
                    return generate_byte_array(val)
                else:
                    # return raw byte array
                    return Literal(types.DataType(types.DataTypes.BYTE, 0), val)
        # create array or dictionary
        elif base.name == 'array_dict':
            # return generated literal
            return generate_array_dict(base)
        # handle inline functions / function data types
        elif base.name == 'inline_function':
            # decide if it is asynchronous or not
            is_async = False
            if base.content[0].type == 'ASYNC':
                is_async = True
            if isinstance(base.content[2], Token):
                parameters = []
            else:
                # generate the parameters (decl_params is 3rd item inward)
                parameters = functions.generate_parameter_list(base.content[2])
            if isinstance(base.content[-1].content[0], ASTNode):
                # ensure function declares a body
                if base.content[-1].content[0].content[0].type != ';':
                    # generate a return type from center (either { main } or => stmt ;)
                    # gen = is generator
                    # if is is not an empty function
                    if isinstance(base.content[-1].content[0].content[1], ASTNode):
                        rt_type, gen = functions.get_return_type(base.content[-1].content[0].content[1])
                    else:
                        rt_type, gen = types.DataType(types.DataTypes.NULL, 0), False
                else:
                    errormodule.throw('semantic_error', 'Inline functions must declare a body', base.content[-1])
                    return
                dt = types.Function(parameters, rt_type, 0, is_async, gen)
                # in function literals, its value is its parameters
                # TODO add body parsing to inline functions
                fbody = base.content[-1].content[0].content[1] if isinstance(base.content[-1].content[0].content[1], ASTNode) else []
                return Literal(dt, fbody)
            else:
                return_type = functions.get_return_from_type(base.content[-1].content[1])
                func = types.Function(parameters, return_type, 0, is_async, False)
                return Literal(types.DataTypeLiteral(func), func)
        elif base.name == 'atom_types':
            tp = generate_type(base)
            # use types to generate a type result
            return Literal(types.DataTypeLiteral(tp), tp)
        # handle lambda generation
        elif base.name == 'lambda':
            # parameter holders
            params = []
            for item in base.content:
                if isinstance(item, ASTNode):
                    # compile parameter from lambda_params
                    if item.name == 'lambda_params':
                        param_content = item.content
                        if param_content[-1].name == 'n_lambda_param':
                            while True:
                                # synthesize parameter object
                                params.append(type('Object', (), {
                                    'name': param_content[1].value if param_content[0].type == ',' else param_content[0].value,
                                    'data_type': generate_type(param_content[-2] if param_content[-1].name == 'n_lambda_param' else param_content[-1])
                                }))
                                # check end condition
                                if param_content[-1].name != 'n_lambda_param':
                                    break
                                # update condition
                                param_content = param_content[-1].content
                        else:
                            # handle lambdas with only 1 parameter
                            params.append(type('Object', (), {'name': item.content[0].value, 'data_type': generate_type(item.content[-1])}))
                    elif item.name == 'expr':
                        util.symbol_table.add_scope()
                        for param in params:
                            util.symbol_table.add_variable(Symbol(param.name, param.data_type, []), item)
                        # generate the expr and lambda Literal
                        expr = generate_expr(item)
                        util.symbol_table.exit_scope()
                        dt = types.Function(params, expr.data_type, 0, False, False, True)
                        return Literal(dt, expr)


###############
# COLLECTIONS #
###############

# decide whether or not an array dict is an array or dict, and generate an output accordingly
def generate_array_dict(array_dict):
    # access array dict builder
    array_dict_builder = array_dict.content[1]
    # if it only contains an expression, it is an array
    if len(array_dict_builder.content) < 2:
        # get the element
        elem = generate_expr(array_dict_builder.content[0])
        # check for tuples
        if isinstance(elem.data_type, types.Tuple):
            return Literal(types.ArrayType(elem.values[0].data_type, len(elem.data_type.values), 0), elem.data_type.values)
        # et = elem data_type
        return Literal(types.ArrayType(elem.data_type, 1, 0), [elem])
    # if the last element's (array_dict_branch) first element is a token
    elif isinstance(array_dict_builder.content[-1].content[0], Token):
        if array_dict_builder.content[-1].content[0].type == ':':
            # raw dict == expr : expr n_dict (as a list)
            raw_dict = [array_dict_builder.content[0]] + array_dict_builder.content[-1].content
            # f_key == first key
            f_key = generate_expr(raw_dict[0])
            # make sure f key can be added to dictionary (not mutable
            if types.mutable(f_key.data_type):
                errormodule.throw('semantic_error', 'Dictionary keys cannot be mutable', raw_dict[0])
            # true dict is made up of the action tree values of the first and third element (expr1, and expr2)
            true_dict = {
                f_key: generate_expr(raw_dict[2])
            }
            kt, vt = f_key.data_type, true_dict[f_key].data_type
            # add any extra elements
            if len(raw_dict) == 4:
                def get_true_dict(sub_dict):
                    nonlocal kt, vt
                    # key-value pair
                    kv_pair = []
                    # iterate through dictionary
                    for item in sub_dict.content:
                        # check for ast nodes
                        if isinstance(item, ASTNode):
                            # extract expr
                            if item.name == 'expr':
                                kv_pair.append(generate_expr(item))
                            # continue adding elements
                            elif item.name == 'n_dict':
                                get_true_dict(item)
                    # type checking
                    # kv1t/kv2t == key-value (pos) type
                    kv1t, kv2t = kv_pair[0].data_type, kv_pair[1].data_type

                    # used to check whether or not the two types can be matches
                    def match(base_type, nt):
                        if base_type == nt:
                            return base_type
                        elif types.coerce(base_type, nt):
                            return base_type
                        nnt = types.dominant(nt, base_type)
                        if nnt:
                            return nnt
                        else:
                            return types.OBJECT_TEMPLATE

                    kt = match(kt, kv1t)
                    vt = match(vt, kv2t)
                    # add to true dictionary
                    true_dict[kv_pair[0]] = kv_pair[1]

                # create dictionary
                get_true_dict(raw_dict[-1])
            # return dictionary literal
            return Literal(types.DictType(kt, vt, 0), true_dict)

        # else assume it is an array and use the list generator
        else:
            if array_dict_builder.content[-1].content[-1].name == 'expr':
                # generate array base
                lst = [generate_expr(array_dict_builder.content[0]), generate_expr(array_dict_builder.content[-1].content[-1])]
                # type check array
                dt = types.dominant(lst[0].data_type, lst[1].data_type)
                if not dt:
                    dt = lst[1].data_type if types.coerce(lst[1].data_type, lst[0].data_type) else types.OBJECT_TEMPLATE
                # return compiled literal
                return Literal(types.ArrayType(dt, 2, 0), lst)
            else:
                # get the first element
                f_elem = generate_expr(array_dict_builder.content[0])
                # reform list
                array_dict.content[1] = type('Object', (), dict(name='list_builder', content=array_dict_builder.content[-1].content[1:]))
                # reuse list generator
                lst = generate_list(array_dict)
                # check data types
                if types.coerce(f_elem.data_type, lst.data_type.element_type):
                    dt = f_elem.data_type
                elif types.coerce(lst.data_type.element_type, f_elem.data_type):
                    dt = lst.data_type.element_type
                else:
                    dt = types.OBJECT_TEMPLATE
                # reformed list classified as array
                return Literal(types.ArrayType(dt, len(lst.value) + 1, 0), [f_elem] + lst.value)


# generate a byte array from value of byte token
def generate_byte_array(bytes_string):
    # convert binary literal to hex literal if necessary and remove prefix on all literals
    bytes_string = (hex(int(bytes_string[2:])) if bytes_string.startswith('0b') else bytes_string)[2:]
    # add an extra 0 if necessary
    bytes_string = '0' + bytes_string if len(bytes_string) % 2 != 0 else bytes_string
    # get each hexadecimal element organized into pairs (and re-add prefix)
    bytes_array = ['0x' + x for x in map(''.join, zip(*[iter(bytes_string)] * 2))]
    # create array literal
    return Literal(types.ArrayType(types.DataType(types.DataTypes.BYTE, 0), len(bytes_array), 0), bytes_array)


# generate a list literal from list astnode
def generate_list(lst):
    # get the internal list builder
    lst = lst.content[1]
    # the list the will hold all the subexpressions
    true_list = []

    # recursive function to extract elements from list_builder
    def get_true_list(sub_list):
        nonlocal true_list
        # iterate through given sub_list
        for item in sub_list.content:
            # if it is an AST
            if isinstance(item, ASTNode):
                # expr == elem
                if item.name == 'expr':
                    # generate expr
                    expr = generate_expr(item)
                    # handle tuples
                    if isinstance(expr.data_type, types.Tuple):
                        for value in expr.data_type.values:
                            true_list.append(value)
                    # add regular value to internal list
                    else:
                        true_list.append(expr)

                elif item.name == 'n_list':
                    # continue collecting from sub list
                    get_true_list(item)

    # generate list value
    get_true_list(lst)
    # data type holder (used to check and acts as elem type)
    # nulls are exempted from data checking as they can be coerced into anything
    dt = None
    for elem in true_list:
        if dt:
            if elem.data_type != dt:
                # check for type coercion
                if not types.coerce(dt, elem.data_type):
                    ndt = types.dominant(elem.data_type, dt)
                    # if it is None
                    if not ndt:
                        dt = types.OBJECT_TEMPLATE
                        break
                    dt = ndt
        else:
            # get root element type (assumed from first element)
            dt = elem.data_type
    return Literal(types.ListType(dt, 0), true_list)


#########################
# INLINE FOR AND ITERATORS #
#########################

# create a comprehension from an inline for
def generate_comprehension(lb):
    # descend into new scope for comprehension
    util.symbol_table.add_scope()
    # arguments for action node
    l_args = []
    # narrow down from FOR ( inline_for_expr ) to inline_for_expr
    lb = lb.content[2]
    # data type of return value from comprehension
    l_type = None
    for item in lb.content:
        if isinstance(item, ASTNode):
            if item.name == 'atom':
                # get iterator from ASTNode (atom)
                la = generate_iterator(item)
                # get type for la
                l_type = la.data_type
                # add to args
                l_args.append(la)
            elif item.name == 'expr':
                # add compiled expr to args
                l_args.append(generate_expr(item))
            elif item.name == 'inline_for_if':
                # compile internal expr (IF expr)
                #                           ^^^^
                cond_expr = generate_expr(item.content[1])
                # check to see if it is conditional
                if cond_expr.data_type != types.DataType(types.DataTypes.BOOL, 0):
                    # throw error if not a boolean
                    errormodule.throw('semantic_error', 'Comprehension filter statement expression does not evaluate to a boolean', item)
                # compile final result and add to args
                l_args.append(ExprNode('ForIf', cond_expr.data_type, cond_expr))
    # exit lambda scope
    util.symbol_table.exit_scope()
    return ExprNode('ForExpr', l_type, *l_args)


# convert iter atom to an Iterator
def generate_iterator(lb_atom):
    # temporary variable to hold the lambda iterator
    iterator = None
    # if the ending of the atom is not a trailer (is token), throw error
    if isinstance(lb_atom.content[-1], Token):
        errormodule.throw('semantic_error', 'Invalid iterator', lb_atom)
    ending = lb_atom.content[-1]
    while ending.name == 'trailer':
        iterator = lb_atom.content[-1]
        if isinstance(iterator.content[-1], Token):
            break
        ending = iterator.content[-1]
    # if the ending of the atom is not a trailer (iterator never assigned), throw error
    if not iterator:
        errormodule.throw('semantic_error', 'Invalid iterator', lb_atom)
    # if the trailer found is not a subscript trailer
    if not iterator.content[0].type == '[':
        errormodule.throw('semantic_error', 'Invalid iterator', lb_atom)
    # extract name from trailer
    iter_name = get_iter_name(iterator.content[1])

    # remove the (by normal standards) malformed trailer from the end of the atom
    def remove_iterator(ast):
        if isinstance(ast.content[-1], ASTNode):
            if ast.content[-1].name == 'trailer':
                if remove_iterator(ast.content[-1]):
                    ast.content.pop()
                    return ast
            return True
        return True

    # generate an atom from the remaining components
    base_atom = generate_atom(remove_iterator(lb_atom))
    # get the data type of the iterator
    # check if enumerable
    if types.enumerable(base_atom.data_type):
        # if it is an array or a list
        if isinstance(base_atom.data_type, types.ArrayType) or isinstance(base_atom.data_type, types.ListType):
            iterator_type = base_atom.data_type.element_type
        # if it is a dictionary
        elif isinstance(base_atom.data_type, types.DictType):
            iterator_type = base_atom.data_type.key_type
        # if is is a string
        elif base_atom.data_type.data_type != types.DataTypes.STRING:
            iterator_type = types.DataType(types.DataTypes.CHAR, 0)
        # assume custom type
        else:
            # get return value of its subscript method
            iterator_type = modules.get_property(base_atom.data_type, '__subscript__').data_type.return_type
    # if it is not enumerable and is not either a dict or list, it is an invalid iterative base
    else:
        errormodule.throw('semantic_error', 'Value must be enumerable', lb_atom)
        return
    sym = Symbol(iter_name, iterator_type, [])
    util.symbol_table.add_variable(sym, lb_atom)
    # arguments: [compiled root atom, Iterator]
    args = [base_atom, sym]
    # return generated iterator
    return ExprNode('Iterator', base_atom.data_type, *args)


# gets the name of the new iterator
def get_iter_name(expr):
    for item in expr.content:
        if isinstance(item, ASTNode):
            # the expression must contain only one token (an identifier)
            if len(item.content) > 1:
                errormodule.throw('semantic_error', 'Invalid iterator', expr)
            # if it is a base, and has a length of 1
            elif item.name == 'base':
                # if it is a token, it is valid (again, only identifier), otherwise error
                if isinstance(item.content[0], Token):
                    # must be identifier
                    if item.content[0].type != 'IDENTIFIER':
                        errormodule.throw('semantic_error', 'Invalid iterator', expr)
                    else:
                        # return value (or name)
                        return item.content[0].value
                else:
                    errormodule.throw('semantic_error', 'Invalid iterator', expr)
            else:
                # recur if it is right size, but not base
                return get_iter_name(item)
