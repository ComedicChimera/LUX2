# token class for ASTs
class Token:
    def __init__(self, type, value, ndx):
        self.type = type
        self.value = value
        self.ndx = ndx

    def __str__(self):
        return "Token('%s', '%s')" % (self.type, self.value)


# default AST node class
class ASTNode:
    def __init__(self, name):
        self.name = name
        self.content = []

    def __str__(self):
        str_string = self.name + ":["
        for item in self.content:
            str_string += str(item)
        return str_string + "]"

