import errormodule
import syc.icg.modules as modules
from syc.icg.table import Symbol
from syc.parser.ASTtools import ASTNode, Token
import util
from syc.icg.action_tree import ActionNode, Identifier, Literal
import syc.icg.types as types
import syc.icg.generators.functions as functions


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
                        method = modules.get_method(distribute_expr.data_type.symbol, '__call__')
                        expr_tree = ActionNode('Distribute', method.data_type.return_type, expr_tree, ActionNode('Call', method.data_type.return_type, method))
                else:
                    expr_tree = ActionNode('Distribute', distribute_expr.data_type.return_type, expr_tree, distribute_expr)
        # if it has a trailer, add to expr root tree
        if isinstance(atom.content[-1], ASTNode) and atom.content[-1].name == 'trailer':
            expr_tree = add_trailer(expr_tree, atom.content[-1])
        return expr_tree
    else:
        # all other elements are ASTNodes
        # if the first element is lambda (as in 'lambda trailer')
        if atom.content[0].name == 'inline_for':
            lb = generate_lambda(atom.content[0])
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
                await = True if item.name == 'await' else False
                # set new to true if object is dynamically allocated / object
                new = True if item.name == 'new' else False
                # create base from atom parts
                # always occurs
                base = generate_base(item) if item.name == 'base' else None
                # add trailer to base
                base = add_trailer(base, item) if item.name == 'trailer' else base
            # if awaited and not an async function, throw an error
            if await and not isinstance(base.data_type, types.IncompleteType):
                errormodule.throw('semantic_error', 'Unable to await anything that is not an asynchronous function', atom)
            elif await:
                base = ActionNode('Await', base.data_type.data_type, base)
            # if instance type is a custom Type or normal data type
            if new and isinstance(base, types.CustomType) | isinstance(base, types.DataType):
                # if it is not a structure of a group
                if base.data_type not in [types.DataType(types.DataTypes.STRUCT, 0), types.DataType(types.DataTypes.GROUP, 0)]:
                    # if it is not a data type
                    if base.data_type != types.DataType(types.DataTypes.DATA_TYPE, 0):
                        # if it is not an integer
                        if base.data_type != types.DataType(types.DataTypes.INT, 0):
                            # all tests failed, not allocatable
                            errormodule.throw('semantic_error', 'Unable to allocate memory for object', atom)
                        else:
                            # malloc for just int size
                            base = ActionNode('Malloc', types.DataType(types.DataTypes.OBJECT, 1), base)
                    else:
                        # return memory allocation with size of type
                        base.data_type.pointers += 1
                        base = ActionNode('Malloc', base.data_type, ActionNode('SizeOf', types.DataType(types.DataTypes.INT, 1), base))
                else:
                    # return object instance
                    base = ActionNode('CreateObjectInstance', types.Instance(base.data_type), base)
            elif new:
                # throw error if list, instance, or dict
                errormodule.throw('semantic_error', 'Unable to dynamically allocate memory for object', atom)
            return base


# move import below to allow for recursive imports
from syc.icg.generators.expr import generate_expr
import syc.icg.generators.structs as structs
import syc.icg.casting as casting


def add_trailer(root, trailer):
    # root with trailer added
    trailer_added = None
    # assume first is token
    # if is function call
    if trailer.content[0].type == '(':
        # if it is a function
        if isinstance(root.data_type, types.Function):
            # handle invalid calls on function pointers
            if root.data_type.pointers != 0:
                errormodule.throw('semantic_error', 'Function pointers are not callable', trailer)
            else:
                parameters = functions.check_parameters(root, trailer.content[1])
                trailer_added = ActionNode('Call', root.data_type.return_type, root, parameters)
        elif isinstance(root.data_type, types.DataType):
            if root.data_type.pointers == 0:
                # call (struct) constructor
                if root.data_type.data_type == types.DataTypes.STRUCT:
                    # check struct generator
                    parameters = structs.check_constructor(root.data_type, trailer.content[1])
                    trailer_added = ActionNode('Constructor', root.data_type, root, parameters)
                elif root.data_type.data_type == types.DataTypes.DATA_TYPE:
                    parameters = trailer.content[1].content
                    if len(parameters) > 1:
                        if parameters[1].name == 'named_params':
                            errormodule.throw('semantic_error', 'Type cast does not accept named parameters',
                                              trailer.content[1])
                        else:
                            errormodule.throw('semantic_error', 'Unable to perform type cast on multiple objects',
                                              trailer.content[1])
                    obj = generate_expr(parameters[0])
                    if isinstance(root, Literal):
                        tp = root.value
                        casting.static_cast(tp, obj)
                        return ActionNode('StaticCast', tp, obj)
                    else:
                        errormodule.warn('Dynamic cast performed in place of static cast', trailer)
                        return ActionNode('DynamicCast', types.DataType(types.DataTypes.OBJECT, 0), root, obj)
                else:
                    errormodule.throw('semantic_error', 'Unable to call non-callable type', trailer)
            else:
                errormodule.throw('semantic_error', 'Unable to call non-callable type', trailer)
        # if is module
        elif isinstance(root.data_type, types.CustomType):
            if root.pointers != 0:
                errormodule.throw('semantic_error', 'Unable to call non-callable type', trailer)
            else:
                constructor = modules.get_constructor(root.data_type.symbol)
                parameters = modules.check_constructor_parameters(constructor, trailer.content[1])
                return ActionNode('Call', root.data_type, constructor, parameters)
        # throw invalid call error
        else:
            errormodule.throw('semantic_error', 'Unable to call non-callable type', trailer)
    # if is subscript
    elif trailer.content[0].type == '[':
        # if root.data_type.pointers > 0:
            # errormodule.throw('semantic_error', 'Unable to subscript/slice a pointer', )
        # handle slicing
        if isinstance(trailer.content[1].content[0], Token):
            expr = generate_expr(trailer.content[1].content[1])
            if expr.data_type.pointers != 0:
                errormodule.throw('semantic_error', 'Subscript cannot be a pointer', trailer)
            if expr.data_type.data_type == types.DataTypes.INT and (isinstance(root.data_type, types.ListType)
                                                                    or isinstance(root.data_type, types.ArrayType)):
                return ActionNode('SliceBegin', root.data_type.element_type, root, expr)
            elif isinstance(root.data_type, types.CustomType):
                method = modules.get_method(root.data_type.symbol, '__slice__')
                if method:
                    functions.check_parameters(method, [None, expr])
                    return ActionNode('Call', method.data_type.return_type, method, expr)
                errormodule.throw('semantic_error', 'Object has no method \'__slice__\'', trailer)
            elif root.data_type.data_type == types.DataTypes.STRING and expr.data_type.data_type == types.DataTypes.INT:
                return ActionNode('SliceBegin', types.DataType(types.DataTypes.CHAR, 0), root, expr)
            # TODO add error message for non-integer slice
            errormodule.throw('semantic_error', 'Unable to perform slice on non slice-able object', trailer)
        # handle slice till end
        elif len(trailer.content[1].content) > 1:
            pass
        # handle traditional subscripting
        else:
            # the only subscriptable components are mutable (except for strings)
            if types.mutable(root.data_type):
                # if not dict, use element type, not value type
                dt = root.data_type.value_type if isinstance(root.data_type, types.DictType) else root.data_type.element_type
                trailer_added = ActionNode('Subscript', dt, generate_expr(trailer.content[1].content[0]), root)
            # if it is a module
            elif root.data_type == types.DataType(types.DataTypes.MODULE, 0):
                # if it has subscript method
                subscript_method = modules.get_method(root.value, '__subscript__')
                if subscript_method:
                    expr = generate_expr(trailer.content[1].content[0])
                    functions.check_parameters(subscript_method, [expr])
                    trailer_added = ActionNode('Call', subscript_method.data_type.return_type, subscript_method, expr)
                # otherwise it is invalid
                else:
                    errormodule.throw('semantic_error', 'Object has no method \'__subscript__\'', trailer)
            # strings members can be subscripted, but they cannot modified
            elif root.data_type == types.DataType(types.DataTypes.STRING, 0):
                trailer_added = ActionNode('Subscript', types.DataType(types.DataTypes.CHAR, 0), generate_expr(trailer.content[1]), root)
            else:
                errormodule.throw('semantic_error', 'Object is not subscriptable', trailer)
    # if it is a get member
    elif trailer.content[0].type == '.':
        pass
    # continue adding trailer
    if isinstance(trailer.content[-1], ASTNode):
        if trailer.content[-1].name == 'trailer':
            return add_trailer(trailer_added, trailer.content[-1])
    # otherwise return completed item
    return trailer_added


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
            sym = util.symbol_table.look_up(Identifier(base.value, False))
            # if it is not able to found in the table, throw an error
            if not sym:
                errormodule.throw('semantic_error', 'Variable used without declaration', ast)
            # otherwise return the raw symbol
            return sym
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
                    return Literal(types.DataTypes.BYTE, hex(int(val[2:])))
            else:
                # if it has more than 2 digits (4 because prefix)
                # MAX 0xFF
                if len(val) > 4:
                    # generate a normal byte array
                    return generate_byte_array(val)
                else:
                    # return raw byte array
                    return Literal(types.DataTypes.BYTE, val)
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
            # generate the parameters (decl_params is 3rd item inward)
            parameters = functions.generate_parameter_list(base.content[2])
            if isinstance(base.content[-1].content[0], ASTNode):
                if base.content[-1].content[0].content[0].type != ';':
                    # if it is not an empty function
                    # generate a return type from center (either { main } or => stmt ;)
                    # gen = is generator
                    rt_type, gen = functions.get_return_type(base.content[-1].content[0].content[1])
                else:
                    errormodule.throw('semantic_error', 'Inline functions must declare a body', base.content[-1])
                    # so pycharm won't complain
                    rt_type, gen = None, False
                dt = types.Function(rt_type, 0, is_async, gen)
                # in function literals, its value is its parameters
                # TODO add body parsing to inline functions
                fbody = base.content[-1].content[0].content[1]
                return Literal(dt, (parameters, fbody))
            else:
                return_type = functions.get_return_from_type(base.content[-1].content[1])
                return Literal(types.DataType(types.DataTypes.DATA_TYPE, 0), types.Function(return_type, 0, is_async, False))
        elif base.name == 'atom_types':
            # use types to generate a type result
            return Literal(types.DataType(types.DataTypes.DATA_TYPE, 0), types.generate_type(base))
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
                            while param_content[-1].name == 'n_lambda_param':
                                # synthesize parameter object
                                params.append(type('Object', (), {'name': item.content[0].value, 'data_type': types.generate_type(item.content[-2])}))
                                param_content = param_content[-1].content
                        else:
                            # handle lambdas with only 1 parameter
                            params.append(type('Object', (), {'name': item.content[0].value, 'data_type': types.generate_type(item.content[-1])}))
                    elif item.name == 'expr':
                        # generate the expr and lambda Literal
                        expr = generate_expr(item)
                        dt = types.Function(expr.data_type, 0, False, False, True)
                        return Literal(dt, (params, expr))


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
        # et = elem data_type
        return Literal(types.ArrayType(elem.data_type, 0), [elem])
    # if the last element's (array_dict_branch) first element is a token (:) assume dict
    elif isinstance(array_dict_builder.content[-1].content[0], Token):
        # raw dict == expr : expr n_dict (as a list)
        raw_dict = [array_dict_builder.content[0]] + array_dict_builder.content[-1].content
        # f_key == first key
        f_key = generate_expr(raw_dict[0])
        # make sure f key can be added to dictionary (not mutable
        if types.mutable(f_key):
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
                    nnt = types.dominant(base_type, nt)
                    if nnt:
                        return nnt
                    else:
                        errormodule.throw('semantic_error', 'All keys/values of a dictionary must be of the same type', sub_dict)

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
        # extract n_list
        array_dict.content[1].content[-1] = array_dict.content[1].content[-1].content[0]
        # reuse list generator
        lst = generate_list(array_dict)
        # reformed list classified as array
        return Literal(types.ArrayType(lst.data_type.element_type,  0), lst.value)


# generate a byte array from value of byte token
def generate_byte_array(bytes_string):
    # convert binary literal to hex literal if necessary and remove prefix on all literals
    bytes_string = (hex(int(bytes_string[2:])) if bytes_string.startswith('0b') else bytes_string)[2:]
    # add an extra 0 if necessary
    bytes_string = '0' + bytes_string if len(bytes_string) % 2 != 0 else bytes_string
    # get each hexadecimal element organized into pairs (and re-add prefix)
    bytes_array = ['0x' + x for x in map(''.join, zip(*[iter(bytes_string)] * 2))]
    # create array literal
    return Literal(types.ArrayType(types.DataTypes.BYTE, Literal(types.DataType(types.DataTypes.INT, 0), '0')), bytes_array)


# generate a list literal from list astnode
def generate_list(lst):
    # get the internal list builder
    lst = lst.content[1]
    # the list the will hold all the subexpressions
    true_list = []

    # recursive function to extract elements from list_builder
    def get_true_list(sub_list):
        # iterate through given sub_list
        for item in sub_list.content:
            # if it is an AST
            if isinstance(item, ASTNode):
                # expr == elem
                if item.name == 'expr':
                    # add to internal list
                    true_list.append(generate_expr(item))
                elif item.name == 'n_list':
                    # continue collecting from sub list
                    get_true_list(item)

    # generate list value
    get_true_list(lst)
    # data type holder (used to check and acts as elem type)
    # nulls are accepted from data checking as they can be coerced into anything
    dt = None
    for elem in true_list:
        if dt:
            if elem.data_type != dt:
                # check for type coercion
                if not types.coerce(dt, elem.data_type):
                    ndt = types.dominant(dt, elem.data_type)
                    # if it is None
                    if not ndt:
                        errormodule.throw('semantic_error', 'All elements of a list/array must be of the same type', lst)
                    dt = ndt
        else:
            # get root element type (assumed from first element)
            dt = elem.data_type
    return Literal(types.ListType(dt, 0), true_list)


#########################
# INLINE FOR AND ITERATORS #
#########################

# create a lambda tree from either a lambda expression or lambda statement
def generate_lambda(lb):
    # descend into new scope for lambda
    util.symbol_table.add_scope()
    # arguments for action node
    l_args = []
    # narrow down from FOR ( lambda_expr ) to lambda_expr
    lb = lb.content[2]
    # data type of return value from lambda (data_type == typeof lambda_atom)
    l_type = None
    for item in lb.content:
        if isinstance(item, ASTNode):
            if item.name == 'atom':
                # get lambda atom from ASTNode (atom)
                la = generate_lambda_atom(item)
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
                    errormodule.throw('semantic_error', 'Lambda if statement expression does not evaluate to a boolean', item)
                # compile final result and add to args
                l_args.append(ActionNode('ForIf', cond_expr.data_type, cond_expr))
    # exit lambda scope
    util.symbol_table.exit_scope()
    return ActionNode('ForExpr', l_type, *l_args)


# convert lambda atom to an Iterator
def generate_lambda_atom(lb_atom):
    # temporary variable to hold the lambda iterator
    iterator = None
    # if the ending of the atom is not a trailer (is token), throw error
    if isinstance(lb_atom.content[-1], Token):
        errormodule.throw('semantic_error', 'Invalid lambda iterator', lb_atom)
    ending = lb_atom.content[-1]
    while ending.name == 'trailer':
        iterator = lb_atom.content[-1]
        if isinstance(iterator.content[-1], Token):
            break
        ending = iterator.content[-1]
    # if the ending of the atom is not a trailer (iterator never assigned), throw error
    if not iterator:
        errormodule.throw('semantic_error', 'Invalid lambda iterator', lb_atom)
    # if the trailer found is not a subscript trailer
    if not iterator.content[0].type == '[':
        errormodule.throw('semantic_error', 'Invalid lambda iterator', lb_atom)
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
            iterator_type = modules.get_method(base_atom.data_type, '__subscript__').data_type.return_type
    # if it is not enumerable and is not either a dict or list, it is an invalid iterative base
    else:
        errormodule.throw('semantic_error', 'Lambda value must be enumerable', lb_atom)
        return
    sym = Symbol(iter_name, iterator_type, [])
    util.symbol_table.add_variable(sym, lb_atom)
    # arguments: [compiled root atom, Iterator]
    args = [base_atom, sym]
    # return generated iterator
    return ActionNode('Iterator', base_atom.data_type, *args)


# gets the name of the new iterator
def get_iter_name(expr):
    for item in expr.content:
        if isinstance(item, ASTNode):
            # the expression must contain only one token (an identifier)
            if len(item.content) > 1:
                errormodule.throw('semantic_error', 'Invalid lambda iterator', expr)
            # if it is a base, and has a length of 1
            elif item.name == 'base':
                # if it is a token, it is valid (again, only identifier), otherwise error
                if isinstance(item.content[0], Token):
                    # must be identifier
                    if item.content[0].type != 'IDENTIFIER':
                        errormodule.throw('semantic_error', 'Invalid lambda iterator', expr)
                    else:
                        # return value (or name)
                        return item.content[0].value
                else:
                    errormodule.throw('semantic_error', 'Invalid lambda iterator', expr)
            else:
                # recur if it is right size, but not base
                return get_iter_name(item)
