from src.parser.ASTtools import ASTNode
import src.errormodule as er
import src.semantics.semantics as semantics
import src.semantics.symbols.tb_util as types

# broken


class AtomParser:
    @staticmethod
    def lambda_atom(atom, sc):
        if not AtomParser.check_lambda_trailer(atom):
            er.throw("semantic_error", "Unable to perform lambda operation without proper iterator.", atom)
        rt_val = AtomParser.parse_atom(AtomParser.get_lambda_return(atom), sc)
        lb_atom = semantics.Lambda(AtomParser.get_lambda_iterator(atom), rt_val)
        lb_atom.return_val = rt_val
        return lb_atom

    @staticmethod
    def get_lambda_return(at):
        for item in at.content:
            if isinstance(item, ASTNode):
                if item.name == "trailer":
                    if not AtomParser.get_lambda_return(item):
                        at.content.pop(-1)
                        return at
        else:
            return False

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

    @staticmethod
    def parse_atom(at, scope):
        if len(at.content) > 1:
            if isinstance(at.content[0], ASTNode):
                return "DETERMINE"
            else:
                return from_expr(at.content[1], scope)
        else:
            def parse_base(base_elem):
                if isinstance(base_elem, ASTNode):
                    if base_elem.name == "string":
                        if base_elem.content[0].type == "CHAR_LITERAL":
                            return semantics.DataTypes.CHAR
                        return semantics.DataTypes.STRING
                    elif base_elem.name == "number":
                        if base_elem.content[0].type == "INTEGER_LITERAL":
                            return semantics.DataTypes.INT
                        return semantics.DataTypes.FLOAT
                    elif base_elem.name == "type_cast":
                        if not isinstance(ASTNode, base_elem.content[0]):
                            type_name = base_elem.content[0].type
                            type_matches = {
                                "CHAR_TYPE": semantics.DataTypes.CHAR,
                                "STRING_TYPE": semantics.DataTypes.STRING,
                                "BOOL_TYPE": semantics.DataTypes.BOOL,
                                "INT_TYPE": semantics.DataTypes.INT,
                                "FLOAT_TYPE": semantics.DataTypes.FLOAT,
                                "BYTE_TYPE": semantics.DataTypes.BYTE
                            }
                            return type_matches[type_name]
                    elif base_elem.name == "list":
                        first_elem = base_elem.content[1].content[0]
                        lst = semantics.ListType()
                        lst.element_type = from_expr(first_elem, scope)
                        return lst
                    elif base_elem.name == "dict":
                        key = base_elem.content[1].content[0]
                        value = base_elem.content[1].content[2]
                        dct = semantics.DictType()
                        dct.key_type = parse_base(key)
                        dct.value_type = from_expr(value, scope)
                        return dct
                    else:
                        return "DETERMINE"
                else:
                    if base_elem.type == "NULL":
                        return None
                    else:
                        return "DETERMINE"

            base = at.content[0].content[0]
            return parse_base(base)


class ExpressionParser:
    @staticmethod
    def parse_with(with_expr, scope):
        return from_expr(with_expr.content[2], scope)

    @staticmethod
    def parse_lambda(expr, scope):
        lb_expr = expr.content[2]
        lb = AtomParser.lambda_atom(lb_expr.content[0], scope)
        for item in lb_expr.content:
            if isinstance(item, ASTNode):
                if item.name == "lambda_if":
                    lb.condition = item
        return lb.return_val

    @staticmethod
    def parse_comp(expr, scope):
        rt_type = ""
        for item in expr.content:
            if isinstance(item, ASTNode):
                if item.name == "atom":
                    rt_type = AtomParser.parse_atom(item, scope)
        return rt_type

    @staticmethod
    def parse_equation(expr, scope):
        current_expr = expr
        while True:
            if len(current_expr.content) < 2:
                current_expr = current_expr.content[0]
            elif current_expr.name == "arithmetic":
                return ExpressionParser.parse_ari(current_expr, scope)
            else:
                return semantics.DataTypes.BOOL

    @staticmethod
    def parse_ari(expr, scope):
        if len(expr.content) > 1:
            ExpressionParser.get_dominant_type(expr)
        else:
            ExpressionParser.parse_ari(expr.content[0], scope)

    @staticmethod
    def get_dominant_type(e):
        pass

    @staticmethod
    def parse_inline_generator(expr, scope):
        base_type = ""
        collection = semantics.ListType()
        for item in expr.content:
            if isinstance(item, ASTNode):
                if item.name == "extension":
                    base_type = types.from_type(item.content[1])
                elif item.name == "inline_gen_effect":
                    for elem in item.content:
                        if isinstance(elem, ASTNode):
                            if elem.name == "assignment_ops":
                                if base_type == "":
                                    collection.data_type = from_expr(item.content[1], scope)
                                else:
                                    collection.data_type = base_type
                                break
                            else:
                                # obtained during type checking/identifier checker
                                collection = "DETERMINE"
        return collection


expressions = {
    "with_expr": ExpressionParser.parse_with,
    "lambda": ExpressionParser.parse_lambda,
    "comprehension": ExpressionParser.parse_comp,
    "equation": ExpressionParser.parse_equation,
    "inline_generator": ExpressionParser.parse_inline_generator
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


