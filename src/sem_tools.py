class Attribute:
    def __init__(self, name, val):
        self.name = name
        self.val = val


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
