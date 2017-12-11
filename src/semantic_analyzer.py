from src.semantics import SemanticNode, SemanticToken, get_attributes
from src.ASTtools import ASTNode, AST


symbol_table = {}


class SemanticAnalyzer:
    def __init__(self, sem_ast):
        self.previous_buffer = []
        self.mode = ""
        self.scope = 0
        self.tree = sem_ast

    def get_next(self, tree):
        for item in tree.content:
            if isinstance(item, SemanticNode):
                yield item
                yield self.get_next(item)
            else:
                yield item

    def declare(self):
        next_item = self.get_next(self.tree)
        while True:
            if isinstance(next_item, SemanticToken):
                if next_item.type == ";":
                    return
            elif next_item.name == "id":
                pass


    def analyze(self):
        for item in self.get_next(self.tree):
            if item.attributes[0].endswith("mode"):
                self.mode = item.attributes[0]
                if self.mode == "var_mode":
                    self.declare()
            if isinstance(item, SemanticNode):
                self.check(item)

    def check(self, item):
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
    SemanticAnalyzer(sem_ast).analyze()
    return ast
