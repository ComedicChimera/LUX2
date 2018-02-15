from src.semantics.symbols.symbol_table import construct_symbol_table
from src.parser.ASTtools import ASTNode, Token
from src.errormodule import throw
from src.semantics.checker.semantic_checker import check
from src.semantics.semantics import SemanticConstruct


# checks to see if contextual statements were placed correctly
def check_context(ast, loop, func):
    for item in ast.content:
        if isinstance(item, ASTNode):
            # update if in loop
            if item.name in ["for_block", "do_block", "lambda_stmt"]:
                check_context(item, True, func)
            # update if in function
            elif item.name == "functional_block":
                check_context(item, loop, True)
            # catch returns not placed in functional region
            elif item.name == "return_stmt" and not func:
                throw("semantic_error", "Unable to return from region", item)
            # catches loop returns not placed in a functional region
            elif item.name in ["break_stmt", "continue_stmt"] and not loop:
                throw("semantic_error", "Invalid loop jump", item)
            # descend
            else:
                check_context(item, loop, func)


def check_for(ast):
    for item in ast.content:
        if isinstance(item, ASTNode):
            if item.name == 'for_block':
                if len(item.content) > 2:
                    has_iter = False
                    has_paren = False
                    for elem in item.content:
                        if isinstance(elem, ASTNode):
                            if elem.name == 'atom':
                                if isinstance(elem.content[0], Token):
                                    if elem.content[0].type == "(":
                                        has_paren = True
                            elif elem.name == 'for_body':
                                if isinstance(elem.content[0], Token):
                                    if elem.content[0].type == "=>":
                                        has_iter = True
                    if has_iter and has_paren:
                        throw('semantic_error', 'Invalid for loop construction', item.content[1])
                    elif not has_iter and not has_paren:
                        throw('semantic_error', 'Invalid for loop construction', item.content[1])
            else:
                check_for(ast)


# the main semantic checker function
def check_ast(ast):
    # construct main symbol table
    table = construct_symbol_table(ast)
    # check for basic contextual statements
    check_context(ast, False, False)
    # run main check function on ast
    check(ast, table)
    # checks for loops for proper formation
    check_for(ast)
    # return object containing table and ast
    return SemanticConstruct(table, ast)
