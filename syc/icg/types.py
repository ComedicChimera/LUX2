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
    MODULE = 9
    ENUM = 10
    INTERFACE = 11

    # object type (parent type for all types)
    OBJECT = 12

    # imported package
    PACKAGE = 13

    # type for holding data type
    DATA_TYPE = 14

    # general data type for byte types
    BYTE = 15

    # null type
    NULL = 16

    # value type
    VALUE = 17


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
    def __init__(self, dt, symbol, interfaces):
        # data type (struct, type, group)
        self.data_type = dt
        # the internal symbol of the custom type
        self.symbol = symbol
        # if it can be iterated through by a for loop & subscripted (list based)
        self.enumerable = True if 'IEnumerable' in interfaces else False
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


# type to hold incomplete types
class IncompleteType:
    def __init__(self, func):
        self.async_func = func
        self.data_type = func.return_type


#####################
# UTILITY FUNCTIONS #
#####################


# check if type can be coerced
def coerce(base_type, unknown):
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
    # object
    if base_type.data_type == DataTypes.OBJECT or unknown.data_type == DataTypes.OBJECT:
        return True
    # if either is a not a raw data type, it does not work
    if not isinstance(base_type, DataType) or not isinstance(unknown, DataType):
        return False
    # if it is a complex or float or long, ints and bool can be coerced
    elif base_type.data_type in {DataTypes.COMPLEX, DataTypes.FLOAT, DataTypes.LONG} and unknown.data_type in {DataTypes.INT, DataTypes.BOOL}:
        return True
    # chars can be coerced to strings
    elif base_type.data_type == DataTypes.STRING and unknown.data_type == DataTypes.CHAR:
        return True
    # check if is null
    elif not unknown.data_type:
        return True
    # check if is byte
    elif unknown.data_type == DataTypes.BYTE:
        return True
    return False


# check to see if type will be able to change the data type of a collection or expression
def dominant(base_type, unknown):
    if base_type == unknown:
        return base_type
    # if neither is object and neither is data type return
    if not isinstance(base_type, DataType) or not isinstance(unknown, DataType):
        if type(base_type) == type(unknown):
            if isinstance(base_type, ListType) or isinstance(base_type, ArrayType):
                return dominant(base_type.element_type, unknown.element_type)
            elif isinstance(base_type, DictType):
                return dominant(base_type.key_type, unknown.key_type) and coerce(base_type.value_type, unknown.value_type)
        return
    # if the types are not equal
    if base_type.pointers != unknown.pointers:
        return
    # object type
    if base_type.data_type == DataTypes.OBJECT or unknown.data_type == DataTypes.OBJECT:
        return unknown if base_type.data_type.data_type != DataTypes.OBJECT else unknown
    # if either is a not a raw data type, it does not work
    if not isinstance(base_type, DataType) or not isinstance(unknown, DataType):
        return
    # check string and char data type
    elif base_type.data_type == DataTypes.STRING and unknown.data_type == DataTypes.CHAR:
        return base_type
    # int overriding
    elif base_type.data_type in {DataTypes.FLOAT, DataTypes.COMPLEX, DataTypes.LONG} and unknown.data_type == DataTypes.INT:
        return base_type
    # bool overriding
    elif base_type.data_type in {DataTypes.FLOAT, DataTypes.COMPLEX, DataTypes.LONG, DataTypes.INT} and unknown.data_type == DataTypes.BOOL:
        return base_type
    # char overriding
    elif base_type.data_type == DataTypes.INT and unknown.data_type == DataTypes.CHAR:
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

