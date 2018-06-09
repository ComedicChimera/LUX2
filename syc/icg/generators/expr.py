from syc.ast.ast import ASTNode, unparse
from syc.icg.action_tree import ExprNode
import errormodule
from syc.icg.table import Package
from copy import copy


def generate_expr(expr):
    # hold the resulting expr
    root = None
    for item in expr.content:
        # only possible value is ASTNode
        # if it is a root ASTNode, generate it
        if item.name == 'or':
            root = generate_logical(item)
        # if the root has a continued expr
        elif item.name == 'n_expr':
            # if it is InlineIf
            if item.content[0].type == '?':
                # root ? val1 : val2
                val1 = generate_logical(item.content[1])
                val2 = generate_logical(item.content[3])
                # ensure root is boolean
                if not types.boolean(root.data_type):
                    errormodule.throw('semantic_error', 'Comparison expression of inline comparison must be a boolean', expr.content[0])
                # get the dominant resulting type
                dt = types.dominant(val1.data_type, val2.data_type)
                if not dt:
                    dt = types.dominant(val2.data_type, val1.data_type)
                    # if neither can be overruled by each other, throw error
                    if not dt:
                        errormodule.throw('semantic_error', 'Types of inline comparison must be similar', item)
                return ExprNode('InlineCompare', dt, root, val1, val2)
            # otherwise, it is Null Coalescence
            else:
                # recursive while loop
                n_expr = item
                while n_expr.name == 'n_expr':
                    # get root expression
                    logical = generate_logical(n_expr.content[1])
                    # ensure the root and logical are coercible / equivalent
                    if types.coerce(root.data_type, logical.data_type):
                        root = ExprNode('NullCoalesce', root.data_type, root, logical)
                    # otherwise it is an invalid null coalescence
                    else:
                        errormodule.throw('semantic_error', 'Types of null coalescing must be similar', expr)
                    # recur
                    n_expr = n_expr.content[-1]
    # return final expr
    return root


# allow for recursive imports
import syc.icg.types as types
import syc.icg.modules as modules
import syc.icg.generators.functions as functions


# operate on logical operator (or, and, xor)
def generate_logical(logical):
    # if it is a comparison, pass it on to the next generator
    if logical.name == 'comparison':
        return generate_comparison(logical)
    # unpack tree if it exists
    if len(logical.content) > 1:
        # hold the unpacked tree
        unpacked_tree = logical.content[:]
        # semi-recursive for loop to unpack tree
        for item in unpacked_tree:
            # if it is an ASTNode
            if isinstance(item, ASTNode):
                # and falls into the 'n' categories
                if item.name.startswith('n'):
                    # unpack it
                    unpacked_tree += unpacked_tree.pop().content
        # root holds the next level downward, op = operator being used
        root, op = generate_logical(unpacked_tree.pop(0)), None
        # iterate through unpacked tree
        for item in unpacked_tree:
            # main tree
            if isinstance(item, ASTNode):
                # get next comparison tree if it is a comparison otherwise get next logical tree
                tree = generate_comparison(item) if item.name == 'comparison' else generate_logical(item)
                # if both are simple data types
                if isinstance(tree.data_type, types.DataType) and isinstance(root.data_type, types.DataType):
                    # check booleans and generate boolean operators
                    if tree.data_type.data_type == types.DataTypes.BOOL and tree.data_type.pointers == 0 and \
                                    root.data_type.data_type == types.DataTypes.BOOL and root.data_type.pointers == 0:
                        root = ExprNode(op, types.DataType(types.DataTypes.BOOL, 0), root, tree)
                        continue
                    # generate bitwise operators
                    else:
                        # extract dominant type and if there is not one, throw error
                        dom = types.dominant(root.data_type, tree.data_type)
                        if dom:
                            if not types.coerce(types.DataType(types.DataTypes.INT, 0), dom):
                                errormodule.throw('semantic_error', 'Unable to apply bitwise %s to object' % op.lower(), logical)
                            root = ExprNode('Bitwise' + op, dom, root, tree)
                        else:
                            if not types.coerce(types.DataType(types.DataTypes.INT, 0), tree.data_type):
                                errormodule.throw('semantic_error', 'Unable to apply bitwise %s to object' % op.lower(), logical)
                            root = ExprNode('Bitwise' + op, tree.data_type, root, tree)
                # handle operator overloading
                elif isinstance(root.data_type, types.CustomType):
                    # get and check method
                    method = modules.get_property(tree.data_type, '__%s__' % op.lower())
                    functions.check_parameters(method, tree, item)
                    if method:
                        root = ExprNode('Call', method.data_type.return_type, method, tree)
                    else:
                        errormodule.throw('semantic_error', 'Object has no method \'__%s__\'' % op.lower(), logical)
                else:
                    errormodule.throw('semantic_error', 'Unable to apply bitwise operator to object', logical)
            # only token is operator
            else:
                name = item.type.lower()
                op = name[0].upper() + name[1:]
        return root
    # otherwise recur to next level down
    else:
        return generate_logical(logical.content[0])


# generate comparison operators
def generate_comparison(comparison):
    # generate shift if it is a shift tree (because the comparison generator is recursive)
    if comparison.name == 'shift':
        return generate_shift(comparison)
    # evaluate comparison if there is one
    if len(comparison.content) > 1:
        # generate inversion operator
        if comparison.name == 'not':
            # generate base tree to invert
            tree = generate_shift(comparison.content[1])
            # check for data types
            if isinstance(tree.data_type, types.DataType):
                # unable to ! pointers
                if tree.data_type.pointers > 0:
                    errormodule.throw('semantic_error', 'The \'!\' operator is not applicable to pointer', comparison)
                # generate normal not operator
                return ExprNode('Not', tree.data_type, tree)
            # generate overloaded not operator
            elif isinstance(tree.data_type, types.CustomType):
                # get and check overloaded not method
                not_method = modules.get_property(tree.data_type, '__not__')
                functions.check_parameters(not_method, tree, comparison)
                if not_method:
                    return ExprNode('Call', not_method.data_type.return_type, not_method, tree)
                else:
                    errormodule.throw('semantic_error', 'Object has no method \'__not__\'', comparison)
            else:
                errormodule.throw('semantic_error', 'The \'!\' operator is not applicable to object', comparison)
        # otherwise generate normal comparison operator
        else:
            # unpack tree into expressions and operators
            unpacked_tree = comparison.content[:]
            for item in unpacked_tree:
                if item.name == 'n_comparison':
                    unpacked_tree += unpacked_tree.pop().content
            # root = first element in unpacked tree, op = operator
            root, op = generate_comparison(unpacked_tree.pop(0)), None
            for item in unpacked_tree:
                # all elements are ASTs
                # not is base expression
                if item.name == 'not':
                    # extract next operator tree
                    n_tree = generate_comparison(item)
                    # check numeric comparison
                    if op in {'<=', '>=', '<', '>'}:
                        if types.numeric(n_tree.data_type) and types.numeric(root.data_type):
                            root = ExprNode(op, types.DataType(types.DataTypes.BOOL, 0), root, n_tree)
                        else:
                            errormodule.throw('semantic_error', 'Unable to use numeric comparison with non-numeric type'
                                              , comparison)
                    # generate standard comparison
                    elif op in {'==', '!=', '===', '!=='}:
                        root = ExprNode(op, types.DataType(types.DataTypes.BOOL, 0), root, n_tree)
                # if it is not a base expression, it is an operators
                elif item.name == 'comparison_op':
                    op = item.content[0].value
            return root
    # otherwise recur
    else:
        return generate_comparison(comparison.content[0])


# generate binary shift operators
def generate_shift(shift):
    # if there is a shift performed
    if len(shift.content) > 1:
        # extract operator-expr list
        unpacked_tree = shift.content[:]
        while unpacked_tree[-1].name == 'n_shift':
            unpacked_tree += unpacked_tree.pop().content
        # get first expression
        root = generate_arithmetic(unpacked_tree.pop(0))
        # check root data type
        if not isinstance(root.data_type, types.DataType):
            errormodule.throw('semantic_error', 'Invalid type for left operand of binary shift', shift.content[0])
        # operator used
        op = ''
        for item in unpacked_tree:
            # ast node => arithmetic expr
            if isinstance(item, ASTNode):
                # generate next tree element
                tree = generate_arithmetic(item)
                # type check element
                if isinstance(tree.data_type, types.DataType):
                    # ensure it is an integer (binary shifts can only be continued by integers)
                    if tree.data_type.data_type == types.DataTypes.INT and tree.data_type.pointers == 0:
                        root = ExprNode(op, root.data_type, root, tree)
                        continue
                errormodule.throw('semantic_error', 'Invalid type for right operand of binary shift', item)
            # token => operator
            else:
                if item.type == '<<':
                    op = 'Lshift'
                elif item.type == '>>':
                    op = 'ARshift'
                else:
                    op = 'LRshift'
        return root
    # otherwise, pass on to arithmetic parser
    else:
        return generate_arithmetic(shift.content[0])


def generate_arithmetic(ari):
    # names of overload methods
    method_names = {
        '+': '__add__',
        '-': '__sub__',
        '*': '__mul__',
        '/': '__div__',
        '%': '__mod__',
        '^': '__pow__'
    }
    # unpack tree in operator sets
    unpacked_tree = ari.content[:]
    while unpacked_tree[-1].name in {'add_sub_op', 'mul_div_mod_op', 'exp_op'}:
        unpacked_tree += unpacked_tree.pop().content
    # root = base tree, op = operator, tree = resulting tree
    root, op, tree = None, None, None
    for item in unpacked_tree:
        # ast => expression
        if isinstance(item, ASTNode):
            # if there is an operator, generate arithmetic tree
            if op:
                # generate next value
                val2 = generate_unary_atom(item) if item.name == 'unary_atom' else generate_arithmetic(item)
                # check operands and extract data type
                dt = check_operands(root.data_type, val2.data_type, op, ari)
                if tree:
                    # operator overloading
                    if isinstance(val2.data_type, types.CustomType):
                        # convert to method name
                        name = method_names[op]
                        method = modules.get_property(val2.data_type, name)
                        # assume method exists
                        tree = ExprNode('Call', dt, method, [tree])
                    # add arguments to previous tree (allow for multiple items)
                    if tree.name == op:
                        tree.arguments.append(val2)
                    # create expression node from tree
                    else:
                        tree = ExprNode(op, dt, tree, val2)
                # create root tree
                else:
                    # operator overloading
                    if isinstance(val2.data_type, types.CustomType):
                        # convert to method name
                        name = method_names[op]
                        method = modules.get_property(val2.data_type, name)
                        tree = ExprNode('Call', dt, method, [root])
                    # default generation
                    else:
                        tree = ExprNode(op, dt, root, val2)
                op, root, = None, tree
            # otherwise, generate root
            else:
                root = generate_unary_atom(item) if item.name == 'unary_atom' else generate_arithmetic(item)
        # token => operator
        else:
            op = item.value
    # ensure tree is initialized
    if not tree:
        tree = root
    return tree


def check_operands(dt1, dt2, operator, ast):
    # check for invalid pointer arithmetic
    if dt1.pointers > 0:
        if isinstance(dt2, types.DataType):
            if dt2.data_type == types.DataTypes.INT and dt2.pointers == 0:
                return dt1
        errormodule.throw('semantic_error', 'Pointer arithmetic can only be performed between an integer and a pointer', ast)
    # check addition operator
    if operator == '+':
        # numeric addition
        if types.numeric(dt1) and types.numeric(dt2):
            if types.coerce(dt1, dt2):
                return dt2
            return dt1
        # list / string concatenation
        elif types.enumerable(dt1) and types.enumerable(dt2):
            if dt1 == dt2:
                return dt1
            # check arrays and lists
            elif (isinstance(dt1, types.ArrayType) or isinstance(dt1, types.ListType)) and \
                    (isinstance(dt2, types.ArrayType) or isinstance(dt2, types.ListType)):
                if dt1.element_type == dt2.element_type:
                    return dt1
            errormodule.throw('semantic_error', 'Unable to apply operator to dissimilar enumerable types', ast)
        errormodule.throw('semantic_error', 'Invalid type(s) for operator \'%s\'' % operator, ast)
    # check multiply operator
    elif operator == '*':
        # numeric multiplication
        if types.numeric(dt1) and types.numeric(dt2):
            if types.coerce(dt1, dt2):
                return dt2
            return dt1
        # string multiplication
        if isinstance(dt1, types.DataType) and isinstance(dt2, types.DataType):
            # we can assume val1's pointers
            if dt2.pointers == 0:
                if dt1.data_type == types.DataTypes.STRING and dt2.data_type == types.DataTypes.INT:
                    return dt1
        errormodule.throw('semantic_error', 'Invalid type(s) for operator \'%s\'' % operator, ast)
    # check all other operators
    else:
        if types.numeric(dt1) and types.numeric(dt2):
            if types.coerce(dt1, dt2):
                return dt2
            return dt1
        errormodule.throw('semantic_error', 'Invalid type(s) for operator \'%s\'' % operator, ast)


def generate_unary_atom(u_atom):
    # generate hold atom
    atom = generate_atom(u_atom.content[-1])
    if len(u_atom.content) > 1:
        # check for packages
        if isinstance(atom, Package):
            errormodule.throw('semantic_error', 'Unable to apply operator to package', u_atom)
            return
        # check for tuples
        if isinstance(atom.data_type, types.Tuple):
            errormodule.throw('semantic_error', 'Unable to apply operator to multiple values', u_atom)
            return
        # check data type literal
        if isinstance(atom.data_type, types.DataTypeLiteral):
            errormodule.throw('semantic_error', 'Unable to apply operator to Data Type literal', u_atom)
            return
        # check for template
        if isinstance(atom.data_type, types.Template):
            errormodule.throw('semantic_error', 'Unable to apply operator to template', u_atom)
            return
        prefix = u_atom.content[0].content[0]
        # handle sine change
        if prefix.type == '-':
            # test for numericality
            if types.numeric(atom.data_type):
                # handle modules
                if isinstance(atom.data_type, types.CustomType):
                    invert_method = modules.get_property(atom.data_type, '__invert__')
                    return ExprNode('Call', invert_method.data_type.return_type, invert_method)
                # change the sine of an element
                else:
                    return ExprNode('ChangeSine', atom.data_type, atom)
            else:
                # throw error
                errormodule.throw('semantic_error', 'Unable to change sine on non-numeric type.', u_atom)
        elif prefix.type == 'AMP':
            dt = copy(atom.data_type)
            # create pointer
            dt.pointers += 1
            # reference pointer
            return ExprNode('Reference', dt, atom)
        # handle deref op
        elif prefix.type == '*':
            do = len(unparse(u_atom.content[0].content[1])) + 1 if len(u_atom.content[0].content) > 1 else 1
            # handle pointer error
            # < because that means there is more dereferencing than there are references to dereference
            if atom.data_type.pointers < do:
                errormodule.throw('semantic_error', 'Unable to dereference a non-pointer', u_atom.content[0])
            elif isinstance(atom.data_type, types.VoidPointer):
                if atom.data_type.pointers <= do:
                    errormodule.throw('semantic_error', 'Unable to dereference void pointer', u_atom.content[0])
                vp = copy(atom.data_type)
                vp.pointers -= 1
                return ExprNode('Dereference', vp, do, atom)
            else:
                dt = copy(atom.data_type)
                dt.pointers -= do
                # return dereference with count
                return ExprNode('Dereference', dt, do, atom)

    else:
        return atom


from syc.icg.generators.atom import generate_atom
