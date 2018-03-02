from enum import Enum


# certain members specified with (->) have in-language interfaces and methods
# this allows for dynamic meta programming
class Property(Enum):
    HASHABLE = 0  # dictionary -> IHashable
    ENUMERABLE = 1  # list -> IEnumerable
    NUMERIC = 2  # integer, float, long, complex
    CALLABLE = 3  # functional -> ICallable
    STRING = 4  # string, char
    BOOLEAN = 5  # bool
    STRUCTURE = 6  # struct, group -> IStructural
    ENUM = 7  # type
    MODULE = 8  # module
    ASYNC = 9  # asynchronous component -> IAsynchronous
    INTERFACE = 10
    RAW = 11  # provided for bytes-like objects
    INSTANCE = 12  # used for instance of objects


class DataType:
    def __init__(self):
        self.properties = []
        self.reference_depth = 0

    # check if dt has property
    def includes(self, prop):
        return prop in self.properties

    # add property to data type
    def add_property(self, prop):
        self.properties.append(prop)

    # reference (either reference operator or new)
    def reference(self):
        self.reference_depth += 1

    # dereference (std deref op)
    def dereference(self):
        if self.reference_depth > 0:
            self.reference_depth -= 1
        else:
            raise Exception('Unable to dereference as non-reference')


# default data types & data structures
# provided by standard library


# int
class Integer(DataType):
    def __init__(self):
        DataType.__init__(self)
        self.properties = [Property.NUMERIC]


# float
class Float(DataType):
    def __init__(self):
        DataType.__init__(self)
        self.properties = [Property.NUMERIC]


# complex
class Complex(DataType):
    def __init__(self):
        DataType.__init__(self)
        self.properties = [Property.NUMERIC]


# long
class Long(DataType):
    def __init__(self):
        DataType.__init__(self)
        self.properties = [Property.NUMERIC]


# str
class String(DataType):
    def __init__(self):
        DataType.__init__(self)
        self.properties = [Property.STRING, Property.ENUMERABLE]


# char
class Char(DataType):
    def __init__(self):
        DataType.__init__(self)
        self.properties = [Property.STRING]


# bool
class Boolean(DataType):
    def __init__(self):
        DataType.__init__(self)
        self.properties = [Property.BOOLEAN]


# byte
class Byte(DataType):
    def __init__(self):
        DataType.__init__(self)
        self.properties = [Property.RAW]


# list
class List(DataType):
    def __init__(self, dt):
        DataType.__init__(self)
        self.properties = [Property.ENUMERABLE]
        self.element_type = dt


# dict
class Dictionary(DataType):
    def __init__(self, kt, vt):
        DataType.__init__(self)
        self.properties = [Property.ENUMERABLE, Property.HASHABLE]
        self.key_type = kt
        self.value_type = vt


# func
class Function(DataType):
    def __init__(self):
        DataType.__init__(self)
        self.properties = [Property.CALLABLE]


# async
class AsyncFunction(DataType):
    def __init__(self):
        DataType.__init__(self)
        self.properties = [Property.CALLABLE, Property.ASYNC]


# struct
class Structure(DataType):
    def __init__(self, name):
        DataType.__init__(self)
        self.properties = [Property.STRUCTURE]
        self.name = name


# type
class Type(DataType):
    def __init__(self):
        DataType.__init__(self)
        self.properties = [Property.STRUCTURE, Property.ENUM]


# interface
class Interface(DataType):
    def __init__(self):
        DataType.__init__(self)
        self.properties = [Property.INTERFACE]


# group (no in-language alias)
class Group(DataType):
    def __init__(self):
        DataType.__init__(self)
        self.properties = [Property.STRUCTURE]


# module
class Module(DataType):
    def __init__(self):
        DataType.__init__(self)
        self.properties = [Property.MODULE, Property.STRUCTURE, Property.ASYNC]


# null
class Null(DataType):
    def __init__(self):
        DataType.__init__(self)
        self.properties = []


# data type literals
class CoreType(DataType):
    def __init__(self, dt):
        DataType.__init__(self)
        self.data_type = dt


# this
class InstancePointer:
    def __init__(self):
        self.instance_of = None


# value
class Value:
    pass


