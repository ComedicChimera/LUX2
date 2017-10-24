#broken

#default AST node class
class ASTNode:
    def __init__(self, name):
        self.name = name
        self.content = []

#token class for ASTs
class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

#cleans AST so that they are more readable
def ResolveAST(ast):
    #template content
    content = []
    for item in ast.content:
        content.append(PruneAST(item))
    #cleaned content
    ast.content = [x for x in content if x != ""]
    #returns correct AST
    return ast

#removes unnecessary branches
def PruneAST(item):
    #checks for tokens
    if(isinstance(item, Token)):
        return item
    #checks for unnecessary branches
    else:
        #removes single item containing branches recursively
        if(len(item.content) == 1):
            if(isinstance(item.content[0], Token)):
                return item.content[0]
            else:
                content = []
                for obj in content:
                    content.append(PruneAST(obj))
                item.content[0].content = content
                return item.content[0]
        #removes empty branches
        elif(len(item.content) == 0):
            return ""
        #returns good ASTs
        else:
            return item