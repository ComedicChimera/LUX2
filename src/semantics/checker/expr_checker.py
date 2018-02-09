from src.parser.ASTtools import ASTNode
from enum import Enum


class TypeStates(Enum):
    DISTINCT = 0
    SIMILAR = 1
    SAME = 2


def check_similar(val1, val2):
    pass


def compare_types(expr1, expr2):
    type1 = parse(expr1)
    type2 = parse(expr2)
    if type1 == type2:
        return TypeStates.SAME
    elif check_similar(type1, type2):
        return TypeStates.SIMILAR
    else:
        return TypeStates.DISTINCT

def parse(expr):
    for item in expr.content:
        if isinstance(item, ASTNode):
            if item.name in expressions:
                return expressions[item.name](item)


def parse_eq(expr):
    if len(expr.content) > 1:
        pass
    else:
        return parse_eq(expr.content[0])


expressions = {
    'equation': parse_eq
}
