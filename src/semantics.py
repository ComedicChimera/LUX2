from enum import Enum


class DataStructure(Enum):
    STRUCT = 0
    INTERFACE = 1
    TYPE = 2
    VARIABLE = 3
    CONSTANT = 4
    MODULE = 5
    FUNCTION = 6
    MACRO = 7


class DataTypes(Enum):
    INT = 0
    FLOAT = 1
    BOOL = 2
    STRING = 3
    CHAR = 5


class DataType:
    def __init__(self):
        self.data_type = DataTypes()
        self.pointer = []


class ListType(DataType):
    def __init__(self):
        DataType.__init__(self)
        self.element_type = DataType()


class DictType(DataType):
    def __init__(self):
        DataType.__init__(self)
        self.key_type = DataType()
        self.value_type = DataType()


class Variable:
    def __init__(self):
        self.name = Identifier()
        self.group = []
        self.modifiers = []
        self.data_structure = DataStructure()


class TypedVariable(Variable):
    def __init__(self):
        Variable.__init__(self)
        self.data_type = DataType()
        self.is_const = False


class Function(Variable):
    def __init__(self):
        Variable.__init__(self)
        self.return_type = DataType()
        self.parameters = []
        self.is_macro = False
        self.is_async = False


class Identifier:
    def __init__(self):
        self.name = ""
        self.is_instance = False
        self.core_type = DataTypes()
