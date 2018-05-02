from syc.parser.ASTtools import ASTNode
from syc.icg.action_tree import ActionNode, Literal
import errormodule
from util import unparse
import syc.icg.tuples as tuples


def generate_expr(expr):
    root = None
    for item in expr.content:
        if isinstance(item, ASTNode):
            if item.name == 'or':
                root = generate_logical(item)
            elif item.name == 'n_expr':
                if item.content[0].type == '?':
                    val1 = generate_logical(item.content[1])
                    val2 = generate_logical(item.content[3])
                    dt = root.data_type
                    if not (root.data_type == val1.data_type == val2.data_type):
                        dt = types.dominant(root.data_type, val1.data_type)
                        if not dt:
                            errormodule.throw('semantic_error', 'Types of inline comparison must be similar', expr)
                        dt = types.dominant(dt, val2.data_type)
                        if not dt:
                            errormodule.throw('semantic_error', 'Types of inline comparison must be similar', expr)
                    return ActionNode('InlineCompare', dt, root, val1, val2)
                else:
                    n_expr = item
                    while n_expr.name == 'n_expr':
                        logical = generate_logical(n_expr.content[1])
                        if logical.data_type == root.data_type:
                            root = ActionNode('NullCoalesce', root.data_type, root, logical)
                        else:
                            dom_type = types.dominant(root.data_type, logical.data_type)
                            if dom_type:
                                root = ActionNode('NullCoalesce', dom_type, root, logical)
                            else:
                                errormodule.throw('semantic_error', 'Types of null coalescing must be similar', expr)
    return root


import syc.icg.types as types
import syc.icg.modules as modules
import syc.icg.generators.functions as functions


def generate_logical(logical):
    if len(logical.content) > 1:
        unpacked_tree = logical.content
        for item in unpacked_tree:
            if isinstance(item, ASTNode):
                if item.name in {'n_or', 'n_xor', 'n_and'}:
                    unpacked_tree += unpacked_tree.pop().content
        root, op = generate_logical(unpacked_tree.pop(0)), None
        for item in unpacked_tree:
            if isinstance(item, ASTNode):
                tree = generate_comparison(item) if item.name == 'comparison' else generate_logical(item)
                if isinstance(tree.data_type, types.DataType) and isinstance(root.data_type, types.DataType):
                    if tree.data_type.data_type == types.DataTypes.BOOL and tree.data_type.pointers == 0 and \
                                    root.data_type.data_type == types.DataTypes.BOOL and root.data_type.pointers == 0:
                        root = ActionNode(op, types.DataType(types.DataTypes.BOOL, 0), root, tree)
                        continue
                    else:
                        root = ActionNode('Bitwise' + op, root.data_type, root, tree)
                elif isinstance(root.data_type, types.CustomType):
                    method = modules.get_method(tree.data_type.symbol, '__%s__' % op.lower())
                    functions.check_parameters(method, tree)
                    if method:
                        root = ActionNode('Call', method.data_type.return_type, method, tree)
                    else:
                        errormodule.throw('semantic_error', 'Object has no method \'__%s__\'' % op.lower(), logical)
                else:
                    errormodule.throw('semantic_error', 'Unable to apply bitwise operator to collection', logical)
            else:
                name = item.type.lower()
                op = name[0].upper() + name[1:]
    else:
        return generate_comparison(logical) if logical.name == 'comparison' else generate_logical(logical.content[0])


def generate_comparison(comparison):
    if len(comparison.content) > 1:
        if comparison.name == 'not':
            tree = generate_shift(comparison)
            if isinstance(tree.data_type, types.DataType):
                return ActionNode('Not', tree.data_type, tree)
            elif isinstance(tree.data_type, types.CustomType):
                not_method = modules.get_method(tree.symbol, '__not__')
                functions.check_parameters(not_method, tree)
                if not_method:
                    return ActionNode('Call', not_method.data_type.return_type, not_method, tree)
                else:
                    errormodule.throw('semantic_error', 'Object has no method \'__not__\'', comparison)
            else:
                errormodule.throw('semantic_error', 'The \'!\' operator is not applicable to object', comparison)
        else:
            unpacked_tree = comparison.content
            for item in unpacked_tree:
                if item.name == 'n_comparison':
                    unpacked_tree += unpacked_tree.pop().content
            root, op = generate_comparison(unpacked_tree.pop(0)), None
            for item in unpacked_tree:
                if item.name == 'not':
                    n_tree = generate_comparison(item)
                    if op in {'<=', '>=', '<', '>'}:
                        if types.numeric(n_tree) and types.numeric(root):
                            root = ActionNode(op, types.DataType(types.DataTypes.BOOL, 0), root, n_tree)
                        else:
                            errormodule.throw('semantic_error', 'Unable to use numeric comparison with non-numeric type'
                                              , comparison)
                elif item.name == 'comparison_op':
                    op = item.content[0].value
            return root
    else:
        return generate_shift(comparison) if comparison.name == 'shift' else generate_comparison(comparison.content[0])


def generate_shift(shift):
    if len(shift.content) > 1:
        unpacked_tree = shift.content
        while unpacked_tree[-1].name == 'n_shift':
            unpacked_tree += unpacked_tree.pop().content
        root = generate_arithmetic(unpacked_tree.pop(0))
        if not isinstance(root.data_type, types.DataType):
            errormodule.throw('semantic_error', 'Invalid type for left operand of binary shift', shift)
        op = ''
        for item in unpacked_tree:
            if isinstance(item, ASTNode):
                tree = generate_arithmetic(item)
                if isinstance(tree.data_type, types.DataType):
                    if tree.data_type.data_type == types.DataTypes.INT and tree.data_type.pointers == 0:
                        root = ActionNode(op, root.data_type, root, tree)
                        continue
                errormodule.throw('semantic_error', 'Invalid type for right operand of binary shift', shift)
            else:
                if item.name == '<<':
                    op = 'Alshift'
                elif item.name == '>>':
                    op = 'Rshift'
                else:
                    op = 'Llshift'
        return root
    else:
        return generate_arithmetic(shift.content[0])


def generate_arithmetic(ari):
    unpacked_tree = ari.content
    while unpacked_tree[-1].name in {'add_sub_op', 'mul_div_mod_op', 'exp_op'}:
        unpacked_tree += unpacked_tree.pop().content
    root, op, tree = None, None, None
    for item in unpacked_tree:
        if isinstance(item, ASTNode):
            if op:
                val2 = generate_unary_atom(item) if item.name == 'unary_atom' else generate_arithmetic(item)
                dt = check_operands(root, val2, op, ari)
                if tree:
                    if tree.name == op:
                        tree.arguments.append(val2)
                    else:
                        tree = ActionNode(op, dt, tree, val2)
                else:
                    tree = ActionNode(op, dt, root, val2)
                op, root, = None, None
            else:
                root = generate_unary_atom(item) if item.name == 'unary_atom' else generate_arithmetic(item)
        else:
            op = item.value
    if not tree:
        tree = root
    return tree


def check_operands(val1, val2, operator, ast):
    if val1.data_type.pointers > 0:
        if isinstance(val2.data_type, types.DataType):
            if val2.data_type.data_type == types.DataTypes.INT and val2.pointers == 0:
                return val1.data_type
        errormodule.throw('semantic_error', 'Pointer arithmetic can only be performed between an integer and a pointer', ast)
    if operator == '+':
        if types.numeric(val1.data_type) and types.numeric(val2.data_type):
            if types.dominant(val1.data_type, val2.data_type):
                return val2.data_type
            return val1.data_type
        elif types.enumerable(val1.data_type) and types.enumerable(val2.data_type):
            if val1.data_type == val2.data_type:
                return val1.data_type
            errormodule.throw('semantic_error', 'Unable to apply operator to dissimilar enumerable types', ast)
        errormodule.throw('semantic_error', 'Invalid type(s) for operator \'%s\'' % operator, ast)
    elif operator == '*':
        if types.numeric(val1.data_type) and types.numeric(val2.data_type):
            if types.dominant(val1.data_type, val2.data_type):
                return val2.data_type
            return val1.data_type
        if isinstance(val1.data_type, types.DataType) and isinstance(val2.data_type, types.DataType):
            # we can assume val1's pointers
            if val2.data_type.pointers == 0:
                if val1.data_type.data_type == types.DataTypes.STRING and val2.data_type.data_type == types.DataTypes.INT:
                    return val1.data_type
        errormodule.throw('semantic_error', 'Invalid type(s) for operator \'%s\'' % operator, ast)
    elif operator in {'-', '%', '^'}:
        if types.numeric(val1.data_type) and types.numeric(val2.data_type):
            if types.dominant(val1.data_type, val2.data_type):
                return val2.data_type
            return val1.data_type
        errormodule.throw('semantic_error', 'Invalid type(s) for operator \'%s\'' % operator, ast)
    return val1.data_type


def generate_unary_atom(u_atom):
    if len(u_atom.content) > 1:
        prefix = u_atom.content[0].content[0]
        # only possibility for ASTNode is "deref_op"
        if isinstance(prefix, ASTNode):
            do = len(unparse(prefix))
            # handle pointer error
            # < because that means there is more derefenceing than there are references to dereference
            if u_atom.content[-1].pointers < do:
                errormodule.throw('semantic_error', 'Dereferencing of non-pointer', u_atom)
            else:
                # extract tree
                tree = None
                atom = generate_atom(u_atom.content[-1])
                # apply dereference
                for _ in range(0, do + 1):
                    atom.data_type.pointers -= 1
                    tree = ActionNode('Dereference', atom.data_type, atom)
                return tree
        else:
            # handle sine change
            if prefix.type == '-':
                # get root atom
                atom = u_atom.content[1]
                # test for numericality
                if types.numeric(atom):
                    # handle modules
                    if isinstance(atom.data_type, types.CustomType):
                        invert_method = modules.get_method(atom.data_type.symbol, '__invert__')
                        return ActionNode('Call', invert_method.data_type.return_type, invert_method)
                    # change the sine of an element
                    else:
                        return ActionNode('ChangeSine', atom.data_type, atom)
                else:
                    # throw error
                    errormodule.throw('semantic_error', 'Unable to change sine on non-numeric type.', u_atom)
            elif prefix.type == 'AMP':
                # get generated atom
                pointer = generate_atom(u_atom.content[1])
                # get pointer
                pointer.data_type.pointers += 1
                # reference pointer
                return ActionNode('Reference', pointer.data_type, pointer)
            elif prefix.type == '~':
                # generate tuple
                root = generate_atom(u_atom.content[1])
                if isinstance(root, Literal):
                    tpl = tuples.create_tuple(root)
                    if not tpl:
                        errormodule.throw('semantic_error', 'Tuple cannot be created from a non enumerable object',
                                          u_atom)
                    tpl = Literal(types.DataType(types.DataTypes.TUPLE, 0), tpl)
                else:
                    if not isinstance(root.data_type, types.ArrayType) and not isinstance(root.data_type, types.ListType):
                        if not isinstance(root.data_type, types.DictType):
                            if root.data_type.pointers != 0 or root.data_type.data_type != types.DataTypes.STRING:
                                errormodule.throw('semantic_error', 'Unable to unwrap non-collection', u_atom)
                    tpl = ActionNode('Unwrap', types.DataType(types.DataTypes.TUPLE, 0), root)
                return tpl
    else:
        return generate_atom(u_atom.content[0])


from syc.icg.generators.atom import generate_atom
