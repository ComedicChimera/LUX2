from syc.parser.ASTtools import ASTNode


def generate_expr(expr):
    for item in expr.content:
        if isinstance(item, ASTNode):
            if item.name == 'atom':
                print(generate_atom(item))
            else:
                generate_expr(item)

from syc.icg.generators.atom import generate_atom
