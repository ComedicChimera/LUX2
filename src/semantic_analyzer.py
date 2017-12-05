from src.ASTtools import ASTNode

class SemanticAnalyzer:
    # global symbol table for the compiler
    symbol_table = {}

    def __init__(self):
        self.scope = 0
        self.semantics = []

    def semantic_assert(self):
        pass

    def match(self, x):
        if isinstance(x, ASTNode):
            if x.name == "block":
                self.scope += 1
                self.evaluate(x)
                self.scope -= 1
        return x

    def evaluate(self, ast):
        for item in ast.content:
            self.match(item)
        return ast


def prove(ast):
    sem = SemanticAnalyzer()
    return sem.evaluate(ast)

