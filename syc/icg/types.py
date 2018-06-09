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

    # general data type for byte types
    BYTE = 11

    # null type
    NULL = 12

    # value type
    VALUE = 13

    # data type literal
    DATA_TYPE = 14

    # package type
    PACKAGE = 15


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
class MapType:
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
    def __init__(self, name, dt, members, interfaces, instance=False):
        # custom type name
        self.name = name
        # data type (struct, enum, module, interface)
        self.data_type = dt
        # pointers
        self.pointers = 0
        # the members of the custom type
        self.members = members
        # create interface set
        self.interfaces = interfaces
        # create separate interfaces list for checking
        self.interface_names = [x.name for x in interfaces]
        # if it can be iterated through by a for loop & subscripted (list based)
        self.enumerable = True if 'IEnumerable' in self.interface_names else False
        # if it can be called with parameters (function based)
        self.callable = True if 'ICallable' in self.interface_names else False
        # if it can be used to store a key-value pair and is ENUMERABLE (dict based)
        self.hashable = True if 'IHashable' in self.interface_names else False
        # if it can be used like number (numeric operator overload)
        self.numeric = True if 'INumeric' in self.interface_names else False
        # if it is an instance
        self.instance = instance

    def update_interface_overloads(self):
        # if it can be iterated through by a for loop & subscripted (list based)
        self.enumerable = True if 'IEnumerable' in self.interface_names else False
        # if it can be called with parameters (function based)
        self.callable = True if 'ICallable' in self.interface_names else False
        # if it can be used to store a key-value pair and is ENUMERABLE (dict based)
        self.hashable = True if 'IHashable' in self.interface_names else False
        # if it can be used like number (numeric operator overload)
        self.numeric = True if 'INumeric' in self.interface_names else False


# type to hold incomplete types
class Future:
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


# used to hold template
class Template:
    def __init__(self, type_list):
        # set the template type
        self.type_list = type_list

    def compare(self, other):
        # check for null, object type
        if not self.type_list:
            return True
        # check by normal type list
        if other not in self.type_list:
            return False
        # passed all tests, assume valid
        return True


# store generic object type
OBJECT_TEMPLATE = Template(None)


class VoidPointer:
    def __init__(self):
        self.data_type = OBJECT_TEMPLATE,
        self.pointers = 1


VOID_PTR = VoidPointer()


class Iterator:
    def __init__(self, dt, variables, root):
        self.data_type = dt
        self.variables = variables
        self.root = root


class Generator:
    def __init__(self, dt):
        self.data_type = dt

#####################
# UTILITY FUNCTIONS #
#####################


# check if type can be coerced
def coerce(base_type, unknown):
    # if there is equality => coercible
    if base_type == unknown:
        return True
    # template coercion
    elif isinstance(base_type, Template):
        return base_type.compare(unknown)
    # package coercion
    if isinstance(base_type, Package) or isinstance(unknown, Package):
        if type(base_type) == type(unknown):
            return True
        return False
    # if pointers don't match up, automatically not equal
    if base_type.pointers != unknown.pointers:
        if isinstance(base_type, DataType) and isinstance(unknown, DataType):
            # str -> char*
            if base_type.data_type == DataTypes.STRING and unknown.data_type == DataTypes.CHAR:
                if base_type.pointers == 0 and unknown.pointers == 1:
                    return True
            # char* -> str
            elif base_type.data_type == DataTypes.CHAR and unknown.data_type == DataTypes.STRING:
                if base_type.pointers == 1 and unknown.pointers == 0:
                    return True
        return False
    # if neither is object and neither is data type return
    if not isinstance(base_type, DataType) and not isinstance(unknown, DataType):
        # check for non data type match ups
        if type(base_type) == type(unknown):
            # check lists
            if isinstance(base_type, ListType) or isinstance(base_type, ArrayType):
                return coerce(base_type.element_type, unknown.element_type)
            # check dictionaries
            elif isinstance(base_type, MapType):
                return coerce(base_type.key_type, unknown.key_type) and coerce(base_type.value_type, unknown.value_type)
            # check custom types
            elif isinstance(base_type, CustomType):
                # check interfaces
                if base_type.data_type == DataTypes.INTERFACE:
                    return interface_coerce(base_type, unknown)
                # check enums
                elif base_type.data_type == DataTypes.ENUM:
                    # make sure they are the same enum
                    if base_type.name != unknown.name or base_type.members != unknown.members:
                        return False
                    # if they are both enum instances, they are valid
                    if base_type.instance and unknown.instance:
                        return True
        return False
    # extract enum member type
    if isinstance(unknown, CustomType) and unknown.data_type == DataTypes.ENUM and hasattr(unknown, 'value'):
        unknown = unknown.value.data_type
    # if either is a not a raw data type, it does not work
    if not isinstance(base_type, DataType) or not isinstance(unknown, DataType):
        return False
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


# check interface based type coercion
def interface_coerce(interface, unknown):
    # interfaces CANNOT be coerced between each other
    if unknown.data_type == DataTypes.INTERFACE:
        return False
    elif unknown.data_type == DataTypes.MODULE:
        # if module directly implements interface
        if interface in unknown.interfaces.values():
            return True
        # if module implicitly implements interface
        for method in interface.members:
            if method not in unknown.members:
                return False
        # assume method implement interface
        return True


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
    if isinstance(dt, ListType) or isinstance(dt, MapType) or isinstance(dt, ArrayType):
        return True
    # return false if not mutable
    return False


# check if element is an enumerable type
def enumerable(dt):
    # if element has pointers, it cannot be enumerable
    if dt.pointers != 0:
        return False
    # if it is a collection
    if isinstance(dt, ListType) or isinstance(dt, ArrayType) or isinstance(dt, MapType):
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
    if isinstance(dt, ListType) or isinstance(dt, ArrayType) or isinstance(dt, MapType):
        return False
    # if it is an enumerable CustomType
    elif isinstance(dt, CustomType):
        return dt.numeric
    # check for invalid data type
    elif not isinstance(dt, DataType):
        return False
    # check if is a number
    elif dt.data_type in {DataTypes.INT, DataTypes.FLOAT, DataTypes.COMPLEX, DataTypes.LONG}:
        return True
    else:
        return False


# check if element is a boolean
def boolean(dt):
    # if element has pointers, it is not numeric
    if dt.pointers != 0:
        return False
    # if it not a simple type
    if not isinstance(dt, DataType):
        return False
    # check if it is a boolean type
    if dt.data_type != DataTypes.BOOL:
        return False
    # passed all checks => default to true
    return True


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
