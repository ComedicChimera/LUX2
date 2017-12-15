from src.ASTtools import ASTNode
import src.variables as variables

symbol_table = {}

scope = 0

scope_num = 0

declarations = {
    "variable_declaration": variables.var_parse
}


def new_scope():
    pass


def add_to_symbol_table(var):
    pass


def construct_symbol_table(ast):
    for item in ast.content:
        if isinstance(item, ASTNode):
            if item.name == "block":
                new_scope()
            construct_symbol_table(item)
        else:
            if item.type in declarations:
                add_to_symbol_table(declarations[item.type](item))


def prove(ast):
    construct_symbol_table(ast)
