import src.semantics.variables as variables
from src.parser.ASTtools import ASTNode
from src.errormodule import throw

symbol_table = []

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
    "async_block": variables.func_parse,
    "constructor_block": variables.func_parse
}


def new_scope():
    global scope
    current_level = symbol_table
    for level in range(scope):
        current_level = current_level[-1]
    current_level.append([])
    scope += 1


def add_to_symbol_table(var):
    current_level = symbol_table
    for level in range(scope):
        current_level = current_level[-1]
    current_level.append(var)


# TODO add special handling for module blocks
# builds the symbol table
def construct_symbol_table(ast):
    global scope
    for item in ast.content:
        if isinstance(item, ASTNode):
            prev_scope = scope
            if item.name == "block":
                new_scope()
            construct_symbol_table(item)
            scope = prev_scope
            if item.name in declarations:
                if item.name in ["func_block", "variable_declaration"]:
                    print(declarations[item.name](item, scope).__dict__)
                    add_to_symbol_table(declarations[item.name](item, scope))
                else:
                    print(declarations[item.name](item).__dict__)
                    add_to_symbol_table(declarations[item.name](item))


# checks to see if contextual statements were placed correctly
def check_context(ast, loop, func, local_scope):
    for item in ast.content:
        if isinstance(item, ASTNode):
            if item.name in ["for_block", "do_block"]:
                check_context(item, True, False, local_scope)
            elif item.name == "func_block":
                pass
            elif item.name == "return_stmt" and not func:
                throw("semantic_error", "Unable to return from region", item)
            elif item.name in ["break_stmt", "continue_stmt"] and not loop:
                throw("semantic_error", "Invalid loop jump", item)
            elif item.name == "block":
                check_context(item, loop, func, local_scope + 1)
            else:
                check_context(item, False, False, local_scope)


# the main semantic checker function
def check(ast):
    construct_symbol_table(ast)
    check_context(ast, False, False, 0)
