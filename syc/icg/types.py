from enum import Enum
from syc.icg.table import Package


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
    MODULE = 8
    ENUM = 9
    INTERFACE = 10

    # object type (parent type for all types)
    OBJECT = 11

    # general data type for byte types
    BYTE = 12

    # null type
    NULL = 13

    # value type
    VALUE = 14


# parent class for all data type objects
class DataType:
    def __init__(self, dt, pointers):
        # internal data type
        self.data_type = dt
        # all pointers to that type (*int would be DataType(DataTypes.INT, 1))
        self.pointers = pointers

    # equality operator override
    def __eq__(self, other):
        if isinstance(other, DataType):
            if other.data_type == self.data_type and other.pointers == self.pointers:
                return True
        return False


# adapted data type class for arrays
class ArrayType:
    def __init__(self, et, count, pointers):
        # data type of array elements
        self.element_type = et
        # array element count
        self.count = count
        # pointers
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
    def __init__(self, parameters, rt, pointers, is_async, is_generator, is_lambda=False):
        # value returned from functions as data type
        self.return_type = rt
        # allow for function pointers
        self.pointers = pointers
        # if the function type is asynchronous
        self.async = is_async
        # if the function is a generator
        self.generator = is_generator
        # if the function is a lambda
        self.is_lambda = is_lambda
        # add parameters
        self.parameters = parameters

    def __eq__(self, other):
        if not isinstance(other, Function):
            return False
        return other.return_type == self.return_type and other.pointers == self.pointers and other.async == self.async and other.parameters == self.parameters


# class to hold all user defined group types
class CustomType:
    def __init__(self, dt, members, interfaces):
        # data type (struct, type, module)
        self.data_type = dt
        # the internal symbol of the custom type
        self.members = members
        # if it can be iterated through by a for loop & subscripted (list based)
        self.enumerable = True if 'IEnumerable' in interfaces else False
        # if it can be called with parameters (function based)
        self.callable = True if 'ICallable' in interfaces else False
        # if it can be used to store a key-value pair and is ENUMERABLE (dict based)
        self.hashable = True if 'IHashable' in interfaces else False
        # if it can be used like number (numeric operator overload)
        self.numeric = True if 'INumeric' in interfaces else False
        # if it is an instance
        self.instance = False


# type to hold incomplete types
class IncompleteType:
    def __init__(self, func):
        self.async_func = func
        self.data_type = func.return_type


# type to hold tuples
class Tuple:
    def __init__(self, values):
        self.values = values


# used to hold data type literals
class DataTypeLiteral:
    def __init__(self, dt):
        self.data_type = dt
        self.pointers = 0

    def __eq__(self, other):
        # "type" data type checking
        if not self.data_type or not other.data_type:
            return True
        return self.data_type == other.data_type


#####################
# UTILITY FUNCTIONS #
#####################


# check if type can be coerced
def coerce(base_type, unknown):
    if base_type == unknown:
        return True
    if isinstance(base_type, Package) or isinstance(unknown, Package):
        if type(base_type) == type(unknown):
            return True
        return False
    # if pointers don't match up, automatically not equal
    if base_type.pointers != unknown.pointers:
        return False
    # if neither is object and neither is data type return
    if not isinstance(base_type, DataType) and not isinstance(unknown, DataType):
        if type(base_type) == type(unknown):
            if isinstance(base_type, ListType) or isinstance(base_type, ArrayType):
                return coerce(base_type.element_type, unknown.element_type)
            elif isinstance(base_type, DictType):
                return coerce(base_type.key_type, unknown.key_type) and coerce(base_type.value_type, unknown.value_type)
        return False
    # if either is a not a raw data type, it does not work
    if not isinstance(base_type, DataType) or not isinstance(unknown, DataType):
        return False
    # object
    if base_type.data_type == DataTypes.OBJECT or unknown.data_type == DataTypes.OBJECT:
        return True
    # null
    if unknown.data_type == DataTypes.NULL:
        return True
    # if it is a complex or float or long, ints and bool can be coerced
    elif base_type.data_type in {DataTypes.COMPLEX, DataTypes.FLOAT, DataTypes.LONG} and unknown.data_type == DataTypes.INT:
        return True
    # coerce float to complex
    elif base_type.data_type == DataTypes.COMPLEX and unknown.data_type == DataTypes.FLOAT:
        return True
    # char overriding
    elif base_type.data_type == DataTypes.INT and unknown.data_type == DataTypes.CHAR:
        return True
    # chars can be coerced to strings
    elif base_type.data_type == DataTypes.STRING and unknown.data_type == DataTypes.CHAR:
        return True
    return False


# get dominant type from two different types
def dominant(base_type, unknown):
    if coerce(base_type, unknown):
        return base_type


# check if element is mutable
def mutable(dt):
    # check pointers
    if dt.pointers != 0:
        return False
    # if it is a list, dict, or array
    if isinstance(dt, ListType) or isinstance(dt, DictType):
        return True
    # return false if not mutable
    return False


# check if element is an enumerable type
def enumerable(dt):
    # if element has pointers, it cannot be enumerable
    if dt.pointers != 0:
        return False
    # if it is a collection
    if isinstance(dt, ListType) or isinstance(dt, ArrayType) or isinstance(dt, DictType):
        return True
    # if it is an enumerable CustomType
    elif isinstance(dt, CustomType):
        return dt.enumerable
    # if it is a string
    elif dt.data_type == DataTypes.STRING:
        return True
    else:
        return False


# check if element is a numeric type
def numeric(dt):
    # if element has pointers, it cannot be enumerable
    if dt.pointers != 0:
        return False
    # if it is a collection
    if isinstance(dt, ListType) or isinstance(dt, ArrayType) or isinstance(dt, DictType):
        return False
    # if it is an enumerable CustomType
    elif isinstance(dt, CustomType):
        return dt.numeric
    # check if is a number
    elif dt.data_type in {DataTypes.INT, DataTypes.FLOAT, DataTypes.COMPLEX, DataTypes.LONG}:
        return True
    else:
        return False


# get the size of a Data Type (non-pointer) in bytes
def get_size(dt):
    data_types = {
        DataTypes.INT: 4,
        DataTypes.FLOAT: 8,
        DataTypes.COMPLEX: 16,
        DataTypes.LONG: 8,
        DataTypes.BOOL: 1,
        DataTypes.BYTE: 1,
        DataTypes.CHAR: 2  # TO BE DETERMINED

    }
    return data_types[dt]

