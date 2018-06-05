import syc.icg.action_tree as action_tree
import syc.icg.types as types
import util

# dictionary containing valid nodes and all evaluation functions
# these functions do not perform any kind of checking as the Nodes have already been checked during their generation
valid_nodes = {
    'Subscript': lambda args: args[1][args[0]],
    'Dereference': lambda args: args[0],  # no change needed, already checked by compiler, dereference only has one arg
    'Reference': lambda args: args[0],  # same as dereference
    'ChangeSine': lambda args: -args[0],
    '+': lambda args: sum(args),
    '-': lambda args: aggregate(lambda a, b: a - b, args),
    '*': lambda args: aggregate(lambda a, b: a * b, args),
    '/': lambda args: aggregate(lambda a, b: a / b, args),
    '%': lambda args: aggregate(lambda a, b: a % b, args),
    '^': lambda args: aggregate(lambda a, b: b ** a, list(reversed(args))),
    'ARshift': lambda args: args[0] >> args[1],
    'LRshift': lambda args: (args[0] % 0x100000000) >> args[1],
    'Lshift': lambda args: args[0] << args[1],
    'Not': lambda args: not args[0],
    '==': lambda args: args[0] == args[1],
    '!=': lambda args: args[0] != args[1],
    '>': lambda args: args[0] > args[1],
    '<': lambda args: args[0] < args[1],
    '>=': lambda args: args[0] >= args[1],
    '<=': lambda args: args[0] <= args[1],
    '===': lambda args: type_compare(args[0], args[1]),
    '!==': lambda args: not type_compare(args[0], args[1]),
    'Or': lambda args: args[0] or args[1],
    'And': lambda args: args[0] and args[1],
    'Xor': lambda args: not args[0] and args[1] or args[0] and not args[1],
    'BitwiseOr': lambda args: bitwise_convert(args[0]) | bitwise_convert(args[1]),
    'BitwiseAnd': lambda args: bitwise_convert(args[0]) & bitwise_convert(args[1]),
    'BitwiseXor': lambda args: bitwise_convert(args[0]) ^ bitwise_convert(args[1]),
    'InlineCompare': lambda args: args[1] if args[0] else args[2],
    'SliceBegin': lambda args: args[0][:args[1]],
    'SliceEnd': lambda args: args[0][args[1]:],
    'Slice': lambda args: args[0][args[1]:args[2]],
    'GetMember': lambda args: args[1]  # value has already been computed during generation
}


# used to apply aggregation based actions to a set of items
# assume len(c) is at least 2
def aggregate(func, c):
    aggr = c[0]
    for item in c[1:]:
        aggr = func(aggr, item)
    return aggr


# used to compare both type and value
def type_compare(a, b):
    return a == b and type(a) == type(b)


# used to make value applicable with python bitwise operators
def bitwise_convert(x):
    if type(x) == str:
        return ord(x)
    return x


# check if expression is a constexpr
def check(expr):
    # check expr nodes
    if isinstance(expr, action_tree.ExprNode):
        # if node is invalid
        if expr.name not in valid_nodes:
            return False
        # if one of the arguments is invalid
        for arg in expr.arguments:
            if not check(arg):
                return False
    # if there is non-constexpr Identifier
    elif isinstance(expr, action_tree.Identifier) and not expr.constexpr:
        return False

    # if it is a Literal or all other checks have passed
    return True


# extract value and check expression
def get_array_bound(expr):
    # run initial check on expression
    if not check(expr):
        return

    # extract a numeric value
    return _extract_value(expr)


# extract value from expression
def _extract_value(expr):
    # extract from ExpressionNode
    if isinstance(expr, action_tree.ExprNode):
        # convert arguments first
        args = list(map(lambda x: _extract_value(x), expr.arguments))
        # ensure all arguments are not none
        for arg in args:
            if not arg and arg != 0:
                return

        # return evaluated value
        return valid_nodes[expr.name](args)
    # extract from Identifier
    elif isinstance(expr, action_tree.Identifier):
        # assume symbol exists
        sym = util.symbol_table.look_up(expr.name)
        # check if it is a static custom type
        if isinstance(sym.data_type, types.CustomType) and not sym.data_type.instance:
            return sym
        # return extracted value from expression
        # assume it has value as all constexpr symbols have value
        return _extract_value(sym.value)
    # extract from Literal
    elif isinstance(expr, action_tree.Literal):
        # extract and return value
        return _extract_literal(expr)


# extract value from literal
def _extract_literal(literal):
    # if it a standard type
    if isinstance(literal.data_type, types.DataType):
        # internal data type of expression
        dt = literal.data_type.data_type
        # if integral
        if dt in {types.DataTypes.INT, types.DataTypes.LONG}:
            return int(literal.value)
        # if floating point
        elif dt == types.DataTypes.FLOAT:
            return float(literal.value)
        # if string
        elif dt in {types.DataTypes.STRING, types.DataTypes.CHAR}:
            return literal.value[1:-1]
        # if boolean
        elif dt == types.DataTypes.BOOL:
            return literal.value == 'true'
        # assume complex
        else:
            return complex(literal.value.replace('i', 'j'))
    # if is an array or list
    elif isinstance(literal.data_type, types.ListType) or isinstance(literal.data_type, types.ArrayType):
        # converted list
        lst = []
        # convert list of expressions to list of values
        for item in literal.value:
            valid_item = check(item)
            # check for invalid items
            if not valid_item and valid_item != 0:
                return
            # append extracted item
            lst.append(_extract_value(item))
        # return generated list
        return lst
    # if it a dictionary
    elif isinstance(literal.data_type, types.DictType):
        # converted dict
        dct = {}
        # convert dictionary of expressions to dictionary of values
        for k, v in literal.value.items():
            valid_k, valid_v = check(k), check(v)
            # check for invalid items
            if not valid_k and valid_k != 0 or not valid_v and valid_v != 0:
                return
            # add value to dictionary
            dct[_extract_value(k)] = _extract_value(v)
        # return generated dictionary
        return dct
    # if it is a data type literal
    elif isinstance(literal.data_type, types.DataTypeLiteral):
        return literal.data_type.data_type
    # all other cases are invalid, so return nothing
