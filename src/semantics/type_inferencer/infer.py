from src.semantics.semantics import TypedVariable
from src.parser.ASTtools import ASTNode


def complete_table(symbol_table):
    for i in range(len(symbol_table)):
        item = symbol_table[i]
        if isinstance(item, TypedVariable):
            if item.data_type == "INFER":
                symbol_table[i].data_type = infer(item.initializer)
        elif isinstance(item, list):
            symbol_table[i] = complete_table(item)
    return symbol_table


expressions = {

}


def infer(expr):
    if expr in expressions:
        return expressions[expr.name](expr)
    else:
        return infer(expr)
