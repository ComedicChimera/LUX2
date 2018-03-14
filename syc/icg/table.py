import syc.icg.types as types
from enum import Enum


# holder class for all used modifiers (generally used by table)
class Modifiers(Enum):
    EXTERNAL = 0
    VOLATILE = 1
    PRIVATE = 2
    PROTECTED = 3
    ABSTRACT = 4
    SEALED = 5
    FINAL = 6


# class representing any declared symbol, not an identifier (variable, function, structure, ect.)
class Symbol:
    def __init__(self, name, groups, data_type, modifiers, members=None):
        self.name = name
        # the groups the symbol is apart of
        self.groups = groups
        self.data_type = data_type
        # modifiers [private, volatile, ect.]
        self.modifiers = modifiers
        if members:
            # members is used for things like structs and groups
            self.members = members


class SymbolTable:
    def __init__(self):
        # main global table
        self.table = []
        # path to current scope (integer positions of sub scopes in each layer)
        self.scope_path = []
        # current working scope
        self.scope = []
        # current position in the working scope
        self.pos = 0

    def add_scope(self):
        # add on new sub scope
        self.scope.append([])
        # update the position
        self.pos += 1
        # add previous position to scope path
        self.scope_path.append(self.pos)
        # enter the new scope
        self.scope = self.scope[self.pos]
        # reset position
        self.pos = 0

    def exit_scope(self):
        # if the working scope has been updated
        updated_scope = False

        # update the main table and update working scope
        def update_table(tb, scope_pos=0):
            # if the there are still more scope paths to follow
            if scope_pos < len(self.scope_path):
                # set the scope path sub section to the updated sub section
                # increment scope_pos to allow for recursion
                # pass in sub table to narrow modification range
                tb[self.scope_path[scope_pos]] = update_table(tb[self.scope_path[scope_pos]], scope_pos + 1)
                # will not execute until table has been updated

                # access outer variable updated_scope
                nonlocal updated_scope
                if not updated_scope:
                    # update scope to current outer table
                    self.scope = tb
                    # set boolean to prevent other layers from incorrectly changing the scope
                    updated_scope = True
                return tb
            # return the current scope
            # updates the scope path
            else:
                self.scope_path.pop()
                return self.scope

        # call with global table
        update_table(self.table)

    # add variable to symbol table
    def add_variable(self, var):
        # TODO compile symbol from variable
        self.scope.append(var)

    # add package to symbol table
    # NOTE packages content is expected to be IR Object
    def add_package(self, pkg):
        # if the package is used, add raw include table to it
        if pkg.used:
            self.scope += pkg.content.symbol_table
        else:
            # neither symbol has groups, name is name, data_type is PACKAGE with no pointers, and members is package IR Object

            # if it is external, give symbol external modifier
            if pkg.external:
                sym = Symbol(pkg.name, [], types.DataType(types.DataTypes.PACKAGE, []), [Modifiers.EXTERNAL], pkg.content)
            else:
                sym = Symbol(pkg.name, [], types.DataType(types.DataTypes.PACKAGE, []), [], pkg.content)
            self.scope.append(sym)

    # find symbol in table
    def look_up(self, symbol):
        pass
