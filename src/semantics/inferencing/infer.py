from src.parser.ASTtools import ASTNode
import src.errormodule as er
import src.semantics.semantics as semantics


class AtomParser:
    @staticmethod
    def lambda_atom(atom):
        if not AtomParser.check_lambda_trailer(atom):
            er.throw("semantic_error", "Unable to perform lambda operation without proper iterator.", atom)
        # TODO calculate return value of lambda
        return [AtomParser.get_lambda_iterator(atom)]

    @staticmethod
    def check_lambda_trailer(atom):
        is_valid = False
        for item in atom.content:
            if isinstance(item, ASTNode):
                if item.name == "trailer":
                    if item.content[0].type == "[":
                        is_valid = True
                    for sub_trailer in item.content:
                        if isinstance(item, ASTNode):
                            if sub_trailer.name == "trailer":
                                is_valid = AtomParser.check_lambda_trailer(sub_trailer)
        return is_valid

    @staticmethod
    def get_lambda_iterator(at):
        for item in at.content:
            if isinstance(item, ASTNode):
                if item.name == "trailer":
                    return AtomParser.get_lambda_iterator(item)
            else:
                if item.type == "[":
                    current = at.content[1]
                    while current.name != "base":
                        if len(current.content) > 1:
                            er.throw("semantic_error", "Invalid lambda iterator", current)
                        elif not isinstance(current.content[0], ASTNode):
                            er.throw("semantic_error", "Invalid lambda iterator", current)
                        current = current.content[0]
                    if isinstance(current.content[0], ASTNode):
                        er.throw("semantic_error", "Invalid lambda iterator", current)
                    elif current.content[0].type != "IDENTIFIER":
                        er.throw("semantic_error", "Invalid lambda iterator", current)
                    return current.content[0].value


class ExpressionParser:
    @staticmethod
    def parse_with(with_expr, scope):
        return from_expr(with_expr.content[2], scope)

    @staticmethod
    def parse_lambda(expr, scope):
        lb_expr = expr.content[2]
        iterator = AtomParser.lambda_atom(lb_expr.content[0])
        lb = semantics.Lambda(iterator, lb_expr.content[2])
        for item in lb_expr.content:
            if isinstance(item, ASTNode):
                if item.name == "lambda_if":
                    lb.condition = item
        return lb


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


