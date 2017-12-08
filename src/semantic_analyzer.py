from src.sem_tools import SemanticNode, SemanticToken
from src.ASTtools import ASTNode
from src.attributes import get_attributes


symbol_table = {}


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
    return ast
