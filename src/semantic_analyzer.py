from src.ASTtools import ASTNode


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

    def semantic_assert(self, ast, context):
        if context == "variable_decl_stmt":
            print(ast.content)
            name = ast.content[1]
            print(name)

    def match(self, x):
        if isinstance(x, ASTNode):
            if x.name == "block":
                self.scope += 1
                self.evaluate(x)
                self.scope -= 1
            elif x.name in self.semantics:
                self.semantic_assert(x, self.semantics[x.name])
        return x

    def evaluate(self, ast):
        for item in ast.content:
            self.match(item)
        return ast


def prove(ast):
    sem = SemanticAnalyzer()
    return sem.evaluate(ast)

