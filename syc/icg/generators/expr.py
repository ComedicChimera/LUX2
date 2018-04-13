from syc.parser.ASTtools import ASTNode
from syc.icg.action_tree import ActionNode, Literal
import errormodule
from util import unparse
import syc.icg.tuples as tuples


def generate_expr(expr):
    for item in expr.content:
        if isinstance(item, ASTNode):
            if item.name == 'unary_atom':
                print(generate_unary_atom(item))
            else:
                generate_expr(item)


import syc.icg.types as types
import syc.icg.modules as modules


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
                        return ActionNode('Call', invert_method.data_type.rt_type, invert_method)
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
                else:
                    empty_tuple = tuples.Tuple()
                    empty_tuple.count = -1  # set to designate it is runtime determined
                    if not isinstance(root.data_type, types.ArrayType) and not isinstance(root.data_type, types.ListType):
                        if not isinstance(root.data_type, types.DictType):
                            if root.data_type.pointers != 0 or root.data_type.data_type != types.DataTypes.STRING:
                                errormodule.throw('semantic_error', 'Unable to unwrap non-collection', u_atom)
                    tpl = ActionNode('Unwrap', empty_tuple, root)
                return tpl


    else:
        return generate_atom(u_atom.content[0])


from syc.icg.generators.atom import generate_atom
