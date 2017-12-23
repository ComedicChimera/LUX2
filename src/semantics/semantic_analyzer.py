import src.semantics.variables as variables
from src.parser.ASTtools import ASTNode

symbol_table = {}

scope = 0

scope_num = 0

declarations = {
    "variable_declaration": variables.var_parse,
    "struct_block": variables.struct_parse,
    "interface_block": variables.struct_parse,
    "type_block": variables.struct_parse,
    "module_block": variables.module_parse,
    "func_block": variables.func_parse,
    "macro_block": variables.macro_parse,
    "async_block": variables.func_parse
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
            if item.name in declarations:
                print(declarations[item.name](item).__dict__)
                add_to_symbol_table(declarations[item.name](item))


# the main semantic checker function
def check(ast):
    construct_symbol_table(ast)
