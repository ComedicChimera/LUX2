class CustomException(Exception):
    pass


# token class for ASTs
class Token:
    def __init__(self, type, value, ndx):
        self.type = type
        self.value = value
        self.ndx = ndx

    def pretty(self):
        return "Token(%s, %s)" % (self.type, self.value)


# default AST node class
class ASTNode:
    def __init__(self, name):
        self.name = name
        self.content = []

    def pretty(self):
        pretty_string = self.name + ":["
        for item in self.content:
            pretty_string += item.pretty() + ","
        return pretty_string[:len(pretty_string) - 1] + "]"


class ConsoleColors:
    MAGENTA = '\033[35m'
    BLUE = '\033[34m'
    GREEN = '\033[32m'
    YELLOW = '\033[93m'
    RED = '\033[31m'
    WHITE = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def set_source_dir(path):
    global source_dir
    source_dir = path

source_dir = "C:/Users/forlo/Desktop/Coding/Github/SyClone"
version = "0.0.1"
