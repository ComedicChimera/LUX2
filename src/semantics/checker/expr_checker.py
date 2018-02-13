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
    content = cond.content[0] + cond.content[1].content

    def check(optype1, optype2, op):
        if op in ['==', '!=', '===', '!==']:
            return 'BOOLEAN'
        elif op in ['>=', '<=', '>', '<']:
            int_type = ['INT', 'LONG', 'COMPLEX', 'FLOAT']
            if optype1 in int_type and optype2 in int_type:
                return 'BOOLEAN'
            throw('semantic_error', 'Operands of the inequality operators must be numeric', cond)
        elif op == 'IN':
            if optype2.startswith('LIST') and optype2.startswith('DICT'):
                if optype1 == optype2.split('_')[1:].join('_'):
                    return 'BOOLEAN'
                throw('semantic_error', 'Collection does not contain type of left hand operand', cond)
            throw('semantic_error', 'Operator IN does not apply to non-collections', cond)

    def parse_not(nt):
        pass

    t1, t2 = parse_not(content[2]), parse_not(content[0])
    rt_type = check(t1, t2, content[1].content[0].type)


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






