import re
#broken

class ASTNode:
    def __init__(self, name):
        self.name = name
        self.content = []


class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

def ResolveAST(ast):
    content = []
    for item in ast.content:
        content.append(PruneAST(item))
    ast.content = [x for x in content if x != ""]
    return ast

def PruneAST(item):
    if(isinstance(item, Token)):
        return item
    else:
        if(len(item.content) == 1):
            if(isinstance(item.content[0], Token)):
                return item.content[0]
            else:
                content = []
                for obj in content:
                    content.append(PruneAST(obj))
                item.content[0].content = content
                return item.content[0]
        elif(len(item.content) == 0):
            return ""
        else:
            return item