from src.semantics import SemanticNode, SemanticToken, get_attributes
from src.ASTtools import ASTNode


symbol_table = {}


class SemanticAnalyzer:
    def __init__(self):
        self.previous_buffer = []
        self.mode = ""
        self.scope = 0

    def check(self, sem_ast):
        pass


def convert(item):
    if isinstance(item, ASTNode):
        attr = get_attributes(item, "node")
        item.content = get_semantic_tree(item)
        return SemanticNode(ASTNode, attr)
    else:
        attr = get_attributes(item, "token")
        return SemanticToken(item, attr)


def get_semantic_tree(ast):
    for item in range(len(ast.content)):
        ast.content[item] = convert(ast.content[item])
    return ast


def prove(ast):
    sem_ast = get_semantic_tree(ast)
    SemanticAnalyzer().check(sem_ast)
    return ast
