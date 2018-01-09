from src.parser.ASTtools import ASTNode


class ExpressionParser:
    @staticmethod
    def parse_with(with_expr, scope):
        return from_expr(with_expr.content[2], scope)

    @staticmethod
    def parse_lambda(expr, scope):
        lb_expr = expr.content[2]


expressions = {
    "with_expr": ExpressionParser.parse_with,
    "lambda": ExpressionParser.parse_lambda
}


def from_expr(expr, scope):
    for item in expr.content:
        if isinstance(item, ASTNode):
            if item.name in expressions.keys():
                func = expressions[item.name]
                return func(item, scope)
            else:
                return from_expr(item, scope)


def from_assignment(assign, scope):
    for item in assign.content:
        if isinstance(item, ASTNode):
            if item.name == "expr":
                return from_expr(item, scope)


