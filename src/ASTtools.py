import re


class ASTNode:
    def __init__(self, name):
        self.name = name
        self.content = []

    def AddContent(self, str_literal):
        clist = str_literal.split("\t")
        print(clist)
        for item in clist:
            if(re.match(r"\[.+\]", item)):
                token_list = item.split(",")
                token = Token(token_list[0][1:], token_list[1][:len(token_list[1])])
                self.content.append(token)
            else:
                fp = item.find("(")
                ast = ASTNode(item[:fp])
                ast.AddContent(item[fp:item.rfind(")")])
                self.content.append(item)

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

def ToASTObj(ast_string):
    fp = ast_string.find("(")
    main_ast = ASTNode(ast_string[:fp])
    main_ast.AddContent(ast_string[fp:ast_string.rfind(")")])
    return ResolveAST(main_ast)

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