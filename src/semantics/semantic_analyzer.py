from src.semantics.symbol_management.symbol_table import construct_symbol_table
from src.semantics.symbol_management.identifiers import check_identifier
from src.parser.ASTtools import ASTNode
from src.errormodule import throw

table = []


# checks to see if contextual statements were placed correctly
def check_context(ast, loop, func, local_scope):
    for item in ast.content:
        if isinstance(item, ASTNode):
            if item.name in ["for_block", "do_block", "switch_block"]:
                check_context(item, True, func, local_scope)
            # broken
            elif item.name == "func_block" or item.name == "async_block":
                func = check_identifier(item, False, table, local_scope)
                if func.return_type:
                    check_context(item, loop, True, local_scope)
                else:
                    check_context(item, loop, False, local_scope)
            elif item.name == "macro_block":
                check_context(item, loop, False, local_scope)
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
    global table
    table = construct_symbol_table(ast)
    check_context(ast, False, False, 0)
