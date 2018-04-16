# all Action Tree related classes


# branch nodes that make up the action tree
# similar to AST Nodes
class ActionNode:
    # func = str (name of function / operation)
    # args = list[sub trees / arguments] (can be Literals, Identifiers or other Action Nodes)
    def __init__(self, func, rt_type, *args):
        self.name = func
        self.arguments = args
        # return type of sub function
        self.data_type = rt_type

    def __str__(self):
        return '(%s, %s){%s}' % (self.name, self.data_type, ', '.join(map(lambda x: str(x), self.arguments)))


# class representing literal value
class Literal:
    # data_type = DataType
    # val = literal value (as literal object)
    def __init__(self, data_type, val):
        self.data_type = data_type
        self.value = val

    def __str__(self):
        return 'Literal{%s, %s}' % (self.data_type, self.value)


# class representing in-expr identifier
class Identifier:
    def __init__(self, name, instance):
        self.name = name
        self.instance = instance
