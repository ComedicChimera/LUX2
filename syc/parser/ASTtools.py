# token class for ASTs
class Token:
    def __init__(self, type, value, ndx):
        self.type = type
        self.value = value
        self.ndx = ndx

    def to_str(self):
        return "Token('%s', '%s')" % (self.type, self.value)


# default AST node class
class ASTNode:
    def __init__(self, name):
        self.name = name
        self.content = []

    def to_str(self):
        str_string = self.name + ":["
        for item in self.content:
            str_string += item.to_str()
        return str_string + "]"

