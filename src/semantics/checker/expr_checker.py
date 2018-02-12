from src.parser.ASTtools import ASTNode
from src.errormodule import throw


def parse_logical(logical):
    def shift(expr):
        return expr.content[0] + expr.content[1].content

    if logical.name in ['or', 'and', 'xor']:
        content = shift(logical)
        if parse_logical(content[0]) != 'BOOLEAN' or parse_logical(content[2]) != 'BOOLEAN':
            parse_logical(content[0])
            return 'BYTES'
        while content[-1].name in ['n_or', 'n_and', 'n_xor']:
            n_elem = content[-1].content[1]
            if parse_logical(n_elem) != 'BOOLEAN':
                return 'BYTES'
        return 'BOOLEAN'
    else:
        return parse_cond(logical)


def parse_cond(cond):
    pass


def parse_atom(atom):
    pass


def parse_n_expr(base_type, n_content, expr):
    if isinstance(n_content[0], ASTNode):
        if base_type != 'BOOLEAN':
            throw('semantic_error', 'The primary operand of the ternary conditional operator must be a boolean', expr.content[0])
        operands = n_content[0].content
        if parse_logical(operands[1]) != parse_logical(operands[3]):
            throw('semantic_error', 'Results of ternary conditional operator must of the same type', expr)
        rt_type = parse_logical(operands[1])
    else:
        if base_type != parse_logical(n_content[1]):
            throw('semantic_error', 'Operands of a null coalescence must be of the same type', expr)
        rt_type = base_type
    if isinstance(n_content[-1], ASTNode):
        if n_content[-1].name == 'n_expr':
            rt_type = parse_n_expr(rt_type, n_content[-1].content, expr)
    return rt_type


def parse(expr):
    if len(expr.content) > 1:
        content = [expr.content[0]] + expr.content[1].content
        if isinstance(content[1], ASTNode):
            if parse_logical(content[0]) != 'BOOLEAN':
                throw('semantic_error', 'The primary operand of the ternary conditional operator must be a boolean', content[0])
            operands = content[1].content
            if parse_logical(operands[1]) != parse_logical(operands[3]):
                throw('semantic_error', 'Results of ternary conditional operator must of the same type', expr)
            rt_type = parse_logical(operands[1])
        else:
            if parse_logical(content[0]) != parse_logical(content[2]):
                throw('semantic_error', 'Operands of a null coalescence must be of the same type', expr)
            rt_type = parse_logical(content[0])
        if isinstance(content[-1], ASTNode):
            if content[-1].name == "n_expr":
                n_content = content[-1].content
                rt_type = parse_n_expr(rt_type, n_content, expr)
        return rt_type
    else:
        parse_logical(expr.content[0])






