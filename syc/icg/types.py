from enum import Enum


# enum representing all simple SyClone types
class DataTypes(Enum):
    INT = 0  # int
    COMPLEX = 1  # complex
    LONG = 2  # long
    FLOAT = 3  # float
    BOOL = 4  # bool
    STRING = 5  # str
    CHAR = 6  # char

    # extended type set
    STRUCT = 7
    GROUP = 8
    MODULE = 9
    ENUM_TYPE = 10
    INTERFACE = 11

    # object type (parent type for all types)
    OBJECT = 12

    # imported package
    PACKAGE = 13

    # type for holding data type
    DATA_TYPE = 14


# parent class for all data type objects
class DataType:
    def __init__(self, dt, pointers):
        # internal data type
        self.data_type = dt
        # all pointers to that type (*int would be DataType(DataTypes.INT, 1))
        self.pointers = pointers


# adapted data type class for lists
class ListType:
    def __init__(self, et, pointers):
        # data type of list elements
        self.element_type = et
        # pointers not to the underlying array, but to the list itself
        self.pointers = pointers


# adapted data type class for dicts
class DictType:
    def __init__(self, kt, vt, pointers):
        self.key_type = kt
        self.value_type = vt
        # same principal as lists
        self.pointers = pointers


# special data type class for functions
class Function:
    def __init__(self, rt, pointers, is_async, is_generator):
        # value returned from functions as data type
        self.return_type = rt
        # allow for function pointers
        self.pointers = pointers
        # if the function type is asynchronous
        self.async = is_async
        # if the function is a generator
        self.generator = is_generator


# class to hold all user defined group types
class CustomType:
    def __init__(self, dt, symbol, interfaces):
        # data type (struct, type, group)
        self.data_type = dt
        # the internal symbol of the custom type
        self.symbol = symbol
        # if it can be iterated through by a for loop & subscripted (list based)
        self.iterable = True if 'IEnumerable' in interfaces else False
        # if it can be called with parameters (function based)
        self.callable = True if 'ICallable' in interfaces else False
        # if it can be used to store a key-value pair and is ENUMERABLE (dict based)
        self.hashable = True if 'IHashable' in interfaces else False
        # if it can be used like number (numeric operator overload)
        self.numeric = True if 'INumeric' in interfaces else False


# type to hold object instances
class Instance:
    def __init__(self, dt):
        # CustomType
        self.data_type = dt
