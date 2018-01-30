from src.semantics.symbols.symbol_table import construct_symbol_table
from src.parser.ASTtools import ASTNode
from src.errormodule import throw
from src.semantics.identifier_checker.id_checker import check_id


# checks to see if contextual statements were placed correctly
def check_context(ast, loop, func, local_scope):
    for item in ast.content:
        if isinstance(item, ASTNode):
            if item.name in ["for_block", "do_block", "switch_block"]:
                check_context(item, True, func, local_scope)
            elif item.name == "functional_block":
                check_context(item, loop, True, local_scope)
            elif item.name == "return_stmt" and not func:
                throw("semantic_error", "Unable to return from region", item)
            elif item.name in ["break_stmt", "continue_stmt"] and not loop:
                throw("semantic_error", "Invalid loop jump", item)
            elif item.name == "block":
                check_context(item, loop, func, local_scope + 1)
            else:
                check_context(item, loop, func, local_scope)


# the main semantic checker function
def check(ast):
    table = construct_symbol_table(ast)
    check_context(ast, False, False, 0)
    check_id(table, ast)
