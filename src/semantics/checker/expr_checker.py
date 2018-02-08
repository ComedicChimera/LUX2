from src.parser.ASTtools import ASTNode
from enum import Enum


class TypeStates(Enum):
    DISTINCT = 0
    SIMILAR = 1
    SAME = 2


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
