from enum import Enum
from util import unparse, symbol_table
from syc.parser.ASTtools import Token


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


# adapted data type class for arrays
class ArrayType:
    def __init__(self, et, pointers):
        # data type of array elements
        self.element_type = et
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
    # if either is a not a raw data type, it does not work
    if not isinstance(base_type, DataType) or not isinstance(unknown, DataType):
        return False
    # if pointers don't match up, automatically not equal
    if base_type.pointers != unknown.pointers:
        return False
    # if it is a complex or float or long, ints and bool can be coerced
    elif base_type.data_type == DataTypes.COMPLEX | DataTypes.FLOAT | DataTypes.LONG and unknown.data_type == DataTypes.INT | DataTypes.BOOL:
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
    # if either is a not a raw data type, it does not work
    if not isinstance(base_type, DataType) or not isinstance(unknown, DataType):
        return
    # if the types are not equal
    if base_type.pointers != unknown.pointers:
        return
    # if it is a string, dominant over all others
    elif unknown.data_type == DataTypes.STRING:
        return unknown
    # int overriding
    elif unknown.data_type == DataTypes.FLOAT | DataTypes.COMPLEX | DataTypes.LONG and base_type.data_type == DataTypes.INT:
        return unknown
    # bool overriding
    elif unknown.data_type == DataTypes.FLOAT | DataTypes.COMPLEX | DataTypes.LONG | DataTypes.INT and base_type.data_type == DataTypes.BOOL:
        return unknown
    # byte gets overrun by everything
    elif base_type.data_type == DataTypes.BYTE:
        return unknown


# check if element is mutable
def mutable(element):
    # if it is a list, dict, or array
    if isinstance(element.data_type, ListType) or isinstance(element.data_type, DictType) or isinstance(element.data_type, ArrayType):
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


# generate type from ast (extension or atom types)
def generate_type(ext):
    pointers = 0
    # handle std types (from extension)
    if ext.name == 'types':
        if ext.content[0].name == 'deref_op':
            # extract data type pointers
            pointers = len(unparse(ext.content[0]))
        # update ext to simple types
            ext = ext.content[-1]  # selects last element (always simple types)
    # if it is token, assume array, list or dict
    if isinstance(ext.content[0], Token):
        # assume array
        if ext.content[0].value == 'ARRAY_TYPE':
            # ext.content[1].content[1] == pure_types -> array_modifier -> types
            et = generate_type(ext.content[1].content[1])
            return ArrayType(et, pointers)
        # assume list
        elif ext.content[0].value == 'LIST_TYPE':
            # ext.content[1].content[1] == pure_types -> list_modifier -> types
            return ListType(generate_type(ext.content[1].content[1]), pointers)
        # assume dict
        else:
            # ext.content[1].content[1] == pure_types -> dict_modifier -> types
            kt, vt = generate_type(ext.content[1].content[1]), generate_type(ext.content[1].content[3])
            # compile dictionary type
            return DictType(kt, vt, pointers)
    else:
        if ext.content[0].name == 'pure_types':
            # return matched pure types
            return DataType({
                'INT_TYPE': DataTypes.INT,
                'BOOL_TYPE': DataTypes.BOOL,
                'BYTE_TYPE': DataTypes.BYTE,
                'FLOAT_TYPE': DataTypes.FLOAT,
                'LONG_TYPE': DataTypes.LONG,
                'COMPLEX_TYPE': DataTypes.COMPLEX,
                'STRING_TYPE': DataTypes.STRING,
                'CHAR_TYPE': DataTypes.CHAR,
                'OBJECT_TYPE': DataTypes.OBJECT
                            }[ext.content[0].content[0].type], pointers)
        else:
            # TODO add member checking
            # unable to do until structs, interfaces, modules, and other aliases have been implemented
            # REMEMBER TO ADD THIS
            pass
