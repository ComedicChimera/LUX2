from src.ASTtools import Token, ASTNode, AST
from enum import Enum

symbol_table = {}


class DataType(Enum):
    INT = 0
    STRING = 1
    CHAR = 2
    FLOAT = 3
    BOOL = 4


class Variable:
    def __init__(self):
        self.name = ""
        self.is_const = False
        self.data_type = DataType()
        self.group = []


class SemanticCheck:
    def get_var_name(self, var):
        return ["", []]

    def get_extension_type(self, ext):
        return ""

    def declare(self, stmt):
        var = Variable()
        if stmt.content[0].type == "AMP":
            var.is_const = True
        name = self.get_var_name(stmt.content[1])
        var.group = name[1]
        var.name = name[0]
        if stmt.content[2].name == "extension":
            var.data_type = self.get_extension_type(stmt.content[2])






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
