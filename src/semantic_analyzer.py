class SemanticAnalyzer:
    # global symbol table for the compiler
    symbol_table = {}

    def __init__(self):
        self.scope = 0

    def evaluate(self, ast):
        return ast


def prove(ast):
    sem = SemanticAnalyzer()
    return sem.evaluate(ast)

