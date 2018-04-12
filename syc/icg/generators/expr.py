from syc.parser.ASTtools import ASTNode
from syc.icg.action_tree import ActionNode
import errormodule
from util import unparse


def generate_expr(expr):
    for item in expr.content:
        if isinstance(item, ASTNode):
            if item.name == 'atom':
                print(generate_atom(item))
            else:
                generate_expr(item)


import syc.icg.types as types
import syc.icg.modules as modules


def generate_unary_atom(u_atom):
    if len(u_atom.content) > 1:
        prefix = u_atom.content[0].content[0]
        if isinstance(prefix, ASTNode):
            do = len(unparse(prefix))
            if u_atom.content[-1].pointers != do:
                errormodule.throw('semantic_error', 'Dereferencing of non-pointer', u_atom)
            else:
                tree = None
                atom = generate_atom(u_atom.content[-1])
                for _ in range(0, do + 1):
                    atom.data_type.pointers -= 1
                    tree = ActionNode('Dereference', atom.data_type, atom)
                return tree
        else:
            if prefix.type == '-':
                atom = u_atom.content[1]
                if types.numeric(atom):
                    if isinstance(atom.data_type, types.CustomType):
                        invert_method = modules.get_method(atom.data_type.symbol, '__invert__')
                        return ActionNode('Call', invert_method.data_type.rt_type, invert_method)
                    else:
                        return ActionNode('ChangeSine', atom.data_type, atom)
                else:
                    # throw error
                    errormodule.throw('semantic_error', 'Unable to change sine on non-numeric type.', u_atom)
    else:
        return generate_atom(u_atom.content[0])


from syc.icg.generators.atom import generate_atom
