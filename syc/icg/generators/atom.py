from syc.parser.ASTtools import ASTNode, Token
from syc.icg.generators.expr import generate_expr
from util import symbol_table as table
from syc.icg.action_tree import ActionNode, Identifier
import syc.icg.types as types
import errormodule
from syc.icg.groups import get_method


def generate_atom(atom):
    # the only component of the atom grammar that begins with token is ( expr ) trailer
    if isinstance(atom.content[0], Token):
        # generate root tree
        expr_tree = generate_expr(atom.content[1])
        # if it has a trailer, add to expr root tree
        if isinstance(atom.content[-1], ASTNode):
            expr_tree = add_trailer(expr_tree)
        return expr_tree
    else:
        # all other elements are ASTNodes
        # if the first element is lambda (as in 'lambda trailer')
        if atom.content[0].name == 'lambda':
            lb = generate_lambda(atom.content[0])
            # if there is extra content, assume trailer and add to lambda root
            if len(atom.content) > 1:
                lb = add_trailer(lb)
                # return compiled lambda
                return lb


#########################
# LAMBDAS AND ITERATORS #
#########################

# create a lambda tree from either a lambda expression or lambda statement
def generate_lambda(lb):
    # descend into new scope for lambda
    table.add_scope()
    # arguments for action node
    l_args = []
    # narrow down from LAMBDA ( lambda_expr ) to lambda_expr
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
            elif item.name == 'lambda_body':
                # TODO add parsing for lambda statements
                pass
            elif item.name == 'lambda_if':
                # compile internal expr (IF expr)
                #                           ^^^^
                cond_expr = generate_expr(item.content[1])
                # check to see if it is conditional
                if cond_expr.data_type != types.DataType(types.DataTypes.BOOL, []):
                    # throw error if not a boolean
                    errormodule.throw('semantic_error', 'Lambda if statement expression does not evaluate to a boolean', item)
                # compile final result and add to args
                l_args.append(ActionNode('If', cond_expr, cond_expr.data_type))
    # exit lambda scope
    table.exit_scope()
    return ActionNode('LambdaExpr', l_args, l_type)


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
    # if is list
    if isinstance(base_atom.data_type, types.ListType):
        iterator_type = base_atom.data_type.element_type
    # if is dict
    elif isinstance(base_atom.data_type, types.DictType):
        iterator_type = base_atom.data_type.key_type
    # if is enumerable custom type
    elif base_atom.data_type.iterable:
        iterator_type = get_method(base_atom, 'subscript').return_type
    # if it is not enumerable and is not either a dict or list, it is an invalid iterative base
    else:
        errormodule.throw('semantic_error', 'Lambda value must be iterable', lb_atom)
        return
    # arguments: [compiled root atom, Iterator]
    args = [base_atom, Identifier(iter_name, iterator_type, False, [], [])]
    # return generated iterator
    return ActionNode('Iterator', args, base_atom.data_type)


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


def add_trailer(root):
    return root
