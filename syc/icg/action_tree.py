# all Action Tree related classes


# branch nodes that make up expressions in Action Tree
# similar to AST Nodes
class ExprNode:
    # func = str (name of function / operation)
    # args = list[sub trees / arguments] (can be Literals, Identifiers or other Action Nodes)
    def __init__(self, func, rt_type, *args):
        self.name = func
        self.arguments = [*args]
        # return type of sub function
        self.data_type = rt_type

    def __str__(self):
        return '(%s, %s){%s}' % (self.name, self.data_type, ', '.join(map(lambda x: str(x), self.arguments)))


# single nodes used to represent statements in Action Tree, like ExprNodes, but without return type
class StatementNode:
    # statement = type of statement
    # args = arguments / components of statement
    def __init__(self, stmt, *args):
        self.statement = stmt
        self.arguments = [*args]

    def __str__(self):
        return self.statement + ' {%s}\n' % ', '.join(map(lambda x: str(x), self.arguments))


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
    def __init__(self, name, data_type):
        self.name = name
        self.data_type = data_type
