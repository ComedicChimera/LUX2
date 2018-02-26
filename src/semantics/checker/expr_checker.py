from src.parser.ASTtools import ASTNode
from src.errormodule import throw
from src.semantics.symbols.types import unparse
from src.semantics.checker.functions import check_inline


lambda_variables = []


def find(var):
    pass


def sanitize(obj_name):
    reserved = ['BOOLEAN', 'INT', 'FLOAT', 'STRING', 'COMPLEX', 'LONG', 'CHAR', 'FUNCTION', 'GENERATOR', 'VALUE', 'DATA_TYPE', 'THIS']
    if obj_name in reserved:
        return '#' + obj_name
    elif any(obj_name.startswith(x) for x in ['ASYNC_', 'LIST_', 'DICT_', 'INSTANCE_']):
        return '#' + obj_name
    return obj_name


def parse_logical(logical):
    if logical.name in ['or', 'and', 'xor']:
        if len(logical.content) == 1:
            return parse_logical(logical.content[0])

        content = logical.content[0] + logical.content[1].content
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
    def parse_not(nt):
        if isinstance(nt.content[0], ASTNode):
            return parse_shift(nt.content[0])
        else:
            if parse_shift(nt.content[1]) != 'BOOLEAN':
                throw('semantic_error', 'Unable to perform not operation on non boolean type', cond)
            return 'BOOLEAN'

    if len(cond.content) == 1:
        parse_not(cond)

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

    t1, t2 = parse_not(content[2]), parse_not(content[0])
    rt_type = check(t1, t2, content[1].content[0].type)
    while content[-1].name == 'n_comparison':
        content = content[-1].content
        rt_type = check(rt_type, parse_not(content[1]), content[0])
    return rt_type


def parse_shift(shift):
    if len(shift.content) == 1:
        return parse_ari(shift.content[0])
    tree = shift.content
    rt_type = None
    while tree[-1].name == "n_shift":
        n_tree = tree.pop()
        tree += n_tree.content
        rt_type = parse_ari(tree.content[-2])
    return rt_type


def get_ari_elements(tree):
    for item in tree.content:
        if isinstance(item, ASTNode):
            if item.name in ['add_sub_op', 'mul_div_mod_op', 'exp_op']:
                tree.append(tree.pop().content)
    return tree


def get_ari_rt(c_type, n_type):
    type_index = ['STRING', 'CHAR', 'COMPLEX', 'FLOAT', 'LONG', 'INT', 'BOOLEAN']
    if c_type in type_index:
        c_ndx = type_index.index(c_type)
        n_ndx = type_index.index(n_type)
        if c_ndx > n_ndx:
            return n_type
        else:
            return c_type
    elif not c_type:
        return n_type
    else:
        return c_type


def parse_ari(ari):
    match_table = {
        '+': {'FLOAT': ['COMPLEX', 'INT', 'FLOAT', 'LONG'],
              'INT': ['COMPLEX', 'INT', 'FLOAT', 'LONG'],
              'LONG': ['COMPLEX', 'INT', 'FLOAT', 'LONG'],
              'COMPLEX': ['COMPLEX', 'INT', 'FLOAT', 'LONG'],
              'STRING': ['STRING', 'CHAR']},
        '-': {'FLOAT': ['COMPLEX', 'INT', 'FLOAT', 'LONG'],
              'INT': ['COMPLEX', 'INT', 'FLOAT', 'LONG'],
              'LONG': ['COMPLEX', 'INT', 'FLOAT', 'LONG'],
              'COMPLEX': ['COMPLEX', 'INT', 'FLOAT', 'LONG']},
        '*': {'FLOAT': ['COMPLEX', 'INT', 'FLOAT', 'LONG'],
              'INT': ['COMPLEX', 'INT', 'FLOAT', 'LONG'],
              'LONG': ['COMPLEX', 'INT', 'FLOAT', 'LONG'],
              'COMPLEX': ['COMPLEX', 'INT', 'FLOAT', 'LONG']},
        '/': {'FLOAT': ['COMPLEX', 'INT', 'FLOAT', 'LONG'],
              'INT': ['COMPLEX', 'INT', 'FLOAT', 'LONG'],
              'LONG': ['COMPLEX', 'INT', 'FLOAT', 'LONG'],
              'COMPLEX': ['COMPLEX', 'INT', 'FLOAT', 'LONG']},
        '^': {'INT': ['INT']}
    }

    def get_expected(tp, op):
        try:
            return match_table[op][tp]
        except KeyError:
            if tp == 'STRING' and op == '*':
                match_table[op] = {'INT': ['INT']}
                return ['INT']
            elif tp.startswith('LIST_') and op == '+':
                return [tp]
            elif tp.startswith('DICT_') and op == '+':
                return [tp]
            return ['MISMATCH', match_table[op]]

    tree = get_ari_elements(ari)
    c_type = None
    expected = None
    rt_type = None
    for item in tree:
        if isinstance(item, ASTNode):
            if item.name in ['term', 'factor']:
                l_type = parse_ari(item)
                if expected:
                    if l_type not in expected:
                        throw('semantic_error', 'Type Mismatch: Expected %s' % ", ".join(expected), item)
                rt_type = get_ari_rt(c_type, l_type)
                c_type = l_type
            elif item.name == 'unary_atom':
                l_type = parse_unary_atom(item)
                if expected:
                    if l_type not in expected:
                        throw('semantic_error', 'Type Mismatch: Expected %s' % ", ".join(expected), item)
                rt_type = get_ari_rt(c_type, l_type)
                c_type = l_type
        else:
            if item.type in ['+', '-', '*', '/', '^']:
                expected = get_expected(c_type, item.type)
                if expected[0] == 'MISMATCH':
                    throw('semantic_error', 'Type Mismatch: Expected %s' % ", ".join(expected[1]), item)
    return rt_type


def is_referenceable(atom):
    needs_trailer = False
    if isinstance(atom.content[0], ASTNode):
        if atom.content[0].name == 'lambda':
            return True
    elif atom.content[0].type == '(':
        expr_val = parse(atom.content[1])
        if expr_val == 'NULL':
            return False
        elif expr_val.endswith('_TYPE'):
            return False
        else:
            return True
    for item in atom.content:
        if item.name in ['await', 'new']:
            return False
        elif item.name == 'base':
            if isinstance(item.content[0], ASTNode):
                if item.content[0].name in ['atom_types', 'inline_function']:
                    needs_trailer = True
            else:
                if item.content[0].type in ['NULL', 'VALUE']:
                    needs_trailer = True
        elif item.name == 'trailer':
            needs_trailer = False
    if needs_trailer:
        return False
    else:
        return True


def parse_unary_atom(u_atom):
    if len(u_atom.content) == 1:
        return parse_atom(u_atom.content[0])
    else:
        prefix = u_atom.content[0].content
        if prefix[0].type == '-':
            a_type = parse_atom(u_atom.content[1])
            if a_type in ['INT', 'FLOAT', 'COMPLEX', 'LONG']:
                return a_type
            else:
                throw('semantic_error', 'Unable to perform sign inversion on non-numeric type', u_atom)
        elif prefix[0].type == 'AMP':
            if not is_referenceable(u_atom.content[1]):
                throw('semantic_error', 'Unable to create reference to non-referenceable value', u_atom.content[1])
            return "*" + parse_atom(u_atom.content[1])
        else:
            prefix = "".join(unparse(prefix))
            a_type = parse_atom(u_atom.content[1])
            if a_type.startswith(prefix):
                return a_type[len(prefix):]
            else:
                throw('semantic_error', 'Unable to dereference a non-reference', u_atom)


def extract_identifier(lb_trailer):
    tree = lb_trailer
    while tree.name != 'base':
        if len(tree) > 1:
            throw('semantic_error', 'Invalid lambda iterator', lb_trailer)
        tree = tree.content[0]
    if isinstance(tree.content[0], ASTNode):
        throw('semantic_error', 'Invalid lambda iterator', lb_trailer)
    else:
        if tree.content[0].type != 'IDENTIFIER':
            throw('semantic_error', 'Invalid lambda iterator', lb_trailer)
        else:
            return tree.content[0].value


def parse_lambda_atom(lb_atom):
    data_type = ''
    trailer = False
    for item in lb_atom.content:
        if isinstance(item, ASTNode):
            if item.name == 'base':
                data_type = parse_base(item)
            elif item.name == 'trailer':
                trailer = True
    has_lambda_trailer = False
    c_trailer = None
    if trailer:
        c_trailer = lb_atom.content[-1]
    else:
        throw('semantic_error', 'Invalid lambda iterator', lb_atom)
    identifier = ''
    while trailer:
        if c_trailer.content[0].type == '[':
            identifier = extract_identifier(c_trailer.content[1])
            has_lambda_trailer = True
        else:
            data_type = match_base(data_type, c_trailer)
        if isinstance(c_trailer.content[-1], ASTNode):
            if c_trailer.content[-1].name == 'trailer':
                c_trailer = c_trailer.content[-1]
                has_lambda_trailer = False
            else:
                trailer = False
    if has_lambda_trailer:
        # TODO add support for custom iterators
        if data_type.startswith('LIST_') or data_type.startswith('DICT_') or data_type == 'GENERATOR':
            lambda_variables.append([identifier, data_type])
            return data_type
    else:
        throw('semantic_error', 'Invalid lambda iterator', lb_atom)


def parse_lambda(lb):
    rt_type = ''
    lambda_expr = lb.content[1]
    for item in lambda_expr:
        if isinstance(item, ASTNode):
            if item.name == 'atom':
                rt_type = parse_lambda_atom(item)
            elif item.name == 'expr':
                parse(item)
            elif item.name == 'lambda_if':
                parse(item.content[1])
    lambda_variables.pop()
    return rt_type


def parse_atom(atom):
    rt_type = ''
    await = False
    is_obj = False
    if isinstance(atom.content[0], ASTNode):
        if atom.content[0].name == 'lambda':
            rt_type = parse_lambda(atom.content[0])
        else:
            for item in atom.content:
                if item.name == 'trailer':
                    rt_type = match_base(rt_type, item.name)
                elif item.name == 'await':
                    await = True
                elif item.name == 'new':
                    is_obj = True
                elif item.name == 'base':
                    rt_type = parse_base(item)
    else:
        return parse(atom.content[1])
    if await:
        if rt_type.startswith('ASYNC_'):
            return rt_type[6:]
        else:
            throw('semantic_error', 'Unable to await non-asynchronous element', atom)
    if is_obj:
        if rt_type.startswith('INSTANCE_'):
            return rt_type[9:]
        else:
            return '*' + rt_type
    return rt_type


def match_base(dt, trailer):
    return dt


def parse_inline_func(i_func):
    check_inline(i_func)
    return 'FUNCTION'


def parse_dict_base(key):
    if key.content[0].name == 'id':
        pass
    else:
        literal = key.content[0].content[0].type
        if literal not in ['HEX_LITERAL', 'BINARY_LITERAL', 'INT_LITERAL']:
            lt = literal.split('_')[0]
        elif literal == 'INT_LITERAL':
            lt = 'INT'
        else:
            lt = 'BYTE'
        content = key.content
        for item in content:
            if isinstance(item, ASTNode):
                if item.name == 'dot_id':
                    match_base(lt, item)


def parse_dict(dct):
    if len(dct.content) < 2:
        return 'NULL'
    dct = dct.content[1]
    kt, vt = parse(dct.content[2]), parse_dict_base(dct.content[0])
    keys = list()
    keys.append(dct.content[0])
    while dct.content[-1].name == 'n_dict':
        dct = dct.content[-1].content
        if kt != parse_dict_base(dct.content[0]):
            throw('semantic_error', 'All dictionary keys must be of the same type', dct)
        elif dct.content[0] in keys:
            throw('semantic_error', 'No dictionary may contain duplicate keys', dct)
        elif vt != parse(dct.content[0]):
            throw('semantic_error', 'Dictionary values must be of the same type', dct)
        keys.append(dct.content[0])
    return 'DICT_%s,%s' % (kt, vt)


def parse_list(lst):
    if len(lst.content) < 2:
        return 'NULL'
    lst = lst.content[1]
    lst_elements = lst.content
    for item in lst_elements:
        if isinstance(item, ASTNode):
            if item.name == 'n_list':
                new_content = lst_elements.pop()
                new_content.pop(0)
                lst_elements += new_content
    dt = ''
    for item in lst_elements:
        if dt == '':
            dt = parse(item)
        elif dt != parse(item):
            throw('semantic_error', 'List elements must all be of the same type', item)
    return "LIST_" + dt


def parse_base(base):
    if isinstance(base.content[0], ASTNode):
        node = base.content[0]
        if node.name == 'string':
            return node.content[0].type.split('_')[0]
        elif node.name == 'byte_literal':
            return 'BYTE'
        elif node.name == 'number':
            if node.content[0].type == 'FLOAT_LITERAL':
                return 'FLOAT'
            else:
                return 'INT'
        elif node.name == 'inline_function':
            return parse_inline_func(node)
        elif node.name == 'list':
            return parse_list(node)
        elif node.name == 'dict':
            return parse_dict(node)
        elif node.name == 'atom_types':
            return 'DATA_TYPE'
    else:
        if base.content[0].type in ['VALUE', 'NULL']:
            return base.content[0].type
        elif base.content[0].type == 'COMPLEX_LITERAL':
            return 'COMPLEX'
        elif base.content[0].type == 'BOOL_LITERAL':
            return 'BOOLEAN'
        elif base.content[0].type == 'IDENTIFIER':
            return find(base.content[0].value)


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
