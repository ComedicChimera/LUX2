from src.semantics.symbol_management.identifiers import check_identifier


class Operator:
    def __init__(self, rt, ac):
        self.returns = rt
        self.accepts = ac


class AcceptType:
    def __init__(self, dt, set_return, overrule):
        self.data_type = dt
        self.set_return = set_return
        self.overrule = overrule


def lambda_comprehension(lb, scope):
    pass


math_operator_table = {
    "+": Operator("INT", [AcceptType("INT", None, None), AcceptType("FLOAT", "FLOAT", None), AcceptType("STRING", "STRING", "STRING")])
}


def check_operator(expr):
    print(expr.content)
    print(expr.name)
    data = math_operator_table[expr.content[1].content[0].type]
    print(data.__dict__)


def math_operator(m, scope):
    if m.content[0].name == "bool":
        return check_identifier(m.content[0], False, [])
    elif m.content[0].name == "atom":
        return check_identifier(m.content[0], False, [])
    elif len(m.content) > 1:
        print(m.name)
        print(m.content)
        return check_operator(m)
    else:
        return math_operator(m.content[0], scope)
