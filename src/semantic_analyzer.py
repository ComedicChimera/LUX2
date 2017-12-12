from src.ASTtools import Token, ASTNode, AST

symbol_table = {}


class SemanticCheck:
    def __init__(self):
        pass

    @staticmethod
    def declare(stmt):
        for item in stmt.content:
            print(item.__dict__)


class SemanticAnalyzer:
    def __init__(self, ast):
        self.ast = ast
        self.semantics = {
            "variable_declaration": SemanticCheck.declare
        }

    def get_next(self, ast):
        for item in ast.content:
            if isinstance(item, AST) or isinstance(item, ASTNode):
                yield item
                for item2 in self.get_next(item):
                    yield item2
            else:
                continue

    def analyze(self):
        for item in self.get_next(self.ast):
            if item.name in self.semantics.keys():
                self.semantics[item.name](item)


def prove(ast):
    SemanticAnalyzer(ast).analyze()
    return ast
