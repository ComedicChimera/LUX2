from src.parser.ASTtools import Token


class Identifier:
    def __init__(self, id_list):
        self.name = id_list[0]
        self.group = id_list[1]
        self.instance = id_list[2]


def generate_group(sub_tree):
    group = []
    for item in sub_tree:
        if isinstance(item, Token):
            if item.type == 'IDENTIFIER':
                group.append(item)
        else:
            group += generate_group(item)
    return group


def compile_id(identifier):
    id_list = ['', [], False]
    for item in identifier.content:
        if isinstance(item, Token):
            if item.type == 'THIS':
                id_list[0] = '@THIS'
                id_list[2] = True
            elif item.type == 'IDENTIFIER':
                id_list[0] = item.value
        else:
            id_list[1] = generate_group(item)
    return Identifier(id_list)
