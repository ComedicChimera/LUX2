from json import loads
from util import source_dir


class SemanticToken:
    def __init__(self, token, attributes):
        self.type = token.type
        self.value = token.value
        self.attributes = attributes


class SemanticNode:
    def __init__(self, node, attributes):
        self.name = node.name
        self.content = node.content
        self.attributes = attributes


def get_attributes(item, context):
    attribute_table = loads(open(source_dir + "/src/config/attributes.json").read())
    if context == "node":
        if item.name in attribute_table:
            return attribute_table[item.name]
    else:
        if item.type in attribute_table:
            return attribute_table[item.type]
