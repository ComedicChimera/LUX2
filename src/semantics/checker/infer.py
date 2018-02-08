from src.semantics.checker.table import tm
from src.parser.ASTtools import ASTNode
from src.semantics.checker.expr_checker import parse


def infer(table):
    for item in table:
        if isinstance(item, list):
            tm.descend()
            infer(item)
            tm.ascend()
        else:
            tm.update()
            if item.data_type == "INFER":
                item.data_type = parse_expr(item)


def parse_expr(expr):
    for item in expr:
        if isinstance(item, ASTNode):
            parse(item)
            return get_type(item)


def get_type(element):
    return element
