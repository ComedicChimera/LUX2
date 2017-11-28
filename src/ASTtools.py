from util import Token
from util import ASTNode


# cleans AST so that they are more readable
def resolve_ast(ast):
    # template content
    content = []
    for item in ast.content:
        content.append(prune_ast(item))
    # cleaned content
    ast.content = [x for x in content if x != ""]
    # returns correct AST
    return ast


# removes unnecessary branches
def prune_ast(item):
    # checks for tokens
    if isinstance(item, Token):
        return item
    # checks for unnecessary branches
    else:
        # removes single item containing branches recursively
        if len(item.content) == 1:
            if isinstance(item.content[0], Token):
                return item.content[0]
            else:
                content = []
                for obj in content:
                    content.append(prune_ast(obj))
                item.content[0].content = content
                return item.content[0]
        # removes empty branches
        elif len(item.content) == 0:
            return ""
        # returns good ASTs
        else:
            return item
