# all Action Tree related classes


# branch nodes that make up the action tree
# similar to AST Nodes
class ActionNode:
    # func = str (name of function / operation)
    # args = list[sub trees / arguments] (can be Literals, Identifiers or other Action Nodes)
    def __init__(self, func, args, rt_type):
        self.name = func
        self.arguments = args
        # return type of sub function
        self.data_type = rt_type


# class representing literal value
class Literal:
    # data_type = DataType
    # val = literal value (as literal object)
    def __init__(self, data_type, val):
        self.data_type = data_type
        self.value = val


# class representing an identifier (variable)
class Identifier:
    # name = str (var name)
    # data_type = DataType
    # is_instance = bool (whether or not it is a member of an instance group, ie. this.x)
    # group = list[Identifier] (describes all parent groups in order from outermost to innermost)
    # scope = list[int] (the region of the program in which this Identifier is valid, list of scope nums to descent to get to the desired identifiers)
    def __init__(self, name, data_type, is_instance, group, mods):
        self.name = name
        self.data_type = data_type
        self.instance = is_instance
        self.group = group
        self.modifiers = mods
