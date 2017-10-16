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
    return main_ast