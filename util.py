import os
import sys

# used for unparse
from syc.ast.ast import Token


# main SyClone error class thrown by the error module and others parts of the compiler
class SyCloneRecoverableError(Exception):
    pass


# where the compiler source is stored
# used for opening files such as grammars and tokens
SOURCE_DIR = os.path.dirname(os.path.realpath(__file__))

# current compiler version
VERSION = '1.0.0'

# the current platform for use when converting to llvm
PLATFORM = sys.platform

# the main file / starting file
# used for building later
build_file = ''


# used to convert AST node back to list of tokens
def unparse(ast):
    unparse_list = []
    for item in ast.content:
        if isinstance(item, Token):
            unparse_list.append(item)
        else:
            unparse_list += unparse(item)
    return unparse_list


# main package class
class Package:
    def __init__(self, name, extern, used, ast):
        self.name = name
        self.is_external = extern
        self.used = used
        self.content = ast

    # beautifying method used for testing
    def to_str(self):
        return 'Package(%s, [%s])' % (self.name, self.content.to_str())


# global symbol table
symbol_table = None
