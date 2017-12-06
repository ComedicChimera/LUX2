from src.ASTtools import ASTNode
from src.errormodule import throw


class Variable:
    def __init__(self, name, properties):
        self.name = name
        self.properties = properties


class SemanticAnalyzer:
    # global symbol table for the compiler
    symbol_table = {}

    def __init__(self):
        self.scope = 0
        self.semantics = ["variable_decl_stmt", "assignment", "atom"]

    def declare(self, var):
        pass

    def semantic_assert(self, ast, context):
        if context == "variable_decl_stmt":
            if len(ast.content) > 2:
                name = ast.content[1]
                self.declare(name)
            else:
                throw("semantic_error", "Unable to determine type of variable", ast.content[1])

    def match(self, x):
        if isinstance(x, ASTNode):
            if x.name == "block":
                self.scope += 1
                self.evaluate(x)
                self.scope -= 1
            elif x.name in self.semantics:
                self.semantic_assert(x, x.name)
            else:
                self.evaluate(x)

    def evaluate(self, ast):
        for item in ast.content:
            self.match(item)
        return ast


def prove(ast):
    sem = SemanticAnalyzer()
    return sem.evaluate(ast)

