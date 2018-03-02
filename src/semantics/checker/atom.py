from src.parser.ASTtools import ASTNode
import src.semantics.checker.types as types
import src.errormodule as er


# assumes sub-expressions will not be passed in -> evaluated by upper-level expression parser
def parse_atom(atom):
    await, new = False
    trailer = None
    base = None
    lb = False
    for item in atom.content:
        if isinstance(item, ASTNode):
            if item.name == 'await':
                await = True
            elif item.name == 'new':
                new = True
            elif item.name == 'trailer':
                trailer = item
            elif item.name == 'base' or item.name == 'lambda':
                base = item
                if item.name == 'lambda':
                    lb = True
    dt = check_trailer(base, trailer, lb)
    return match_prefix(dt, await, new, atom)


def parse_base(base):
    pass


def parse_lambda(lb):
    pass


def check_trailer(base, trailer, is_lambda):
    return trailer


def match_prefix(data_type, awaited, is_memset, atom):
    if not data_type.includes(types.Property.ASYNC) and awaited:
        er.throw('semantic_error', 'Unable to await non-asynchronous element', atom)
    elif is_memset:
        if data_type.includes(types.Property.STRUCTURE):
            data_type.add_property(types.Property.INSTANCE)
            return data_type
        elif isinstance(data_type, types.CoreType):
            return data_type.data_type
        else:
            er.throw('semantic_error', 'Unable to dynamically allocate a non-data type', atom)
    return data_type
