from enum import Enum
import errormodule


# holder class for all used modifiers (generally used by table)
class Modifiers(Enum):
    EXTERNAL = 0
    LOCK = 1
    PRIVATE = 2
    PARTIAL = 3
    PROPERTY = 4

    # special modifiers for variables
    CONSTANT = 5
    CONSTEXPR = 6

    # special modifier denoting a deleted symbol
    DELETED = 7


# class representing any declared symbol, not an identifier (variable, function, structure, ect.)
class Symbol:
    def __init__(self, name, data_type, modifiers, value=None, instance=False, inherits=None):
        self.name = name
        # data type holds members in the case of custom types
        self.data_type = data_type
        # modifiers [private, volatile, ect.]
        # unwrap to fix weird bug (not sure why it was broken)
        self.modifiers = [*modifiers]
        if value:
            # members is used for things like structs and modules
            self.value = value
        # if it is a module
        if inherits:
            self.inherits = inherits
        # whether or not variable is instance member
        self.instance = instance

    # used to compare self to another symbol
    def compare(self, var):
        if var == self.name:
            return True
        return False


class Package:
    def __init__(self, name, symbol_table, action_tree):
        self.name = name
        self.data_type = DataTypes.PACKAGE
        self.pointers = 0

    def get_member(self, name):
        pass

    def open(self):
        pass


from syc.icg.types import DataTypes


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

    # adds the new scope to the table
    def update_scope(self, tb, scope_pos=0):
        if scope_pos < len(self.scope_path):
            tb[self.scope_path[scope_pos]] = self.update_scope(tb[self.scope_path[scope_pos]], scope_pos + 1)
            return tb
        else:
            return self.scope

    def add_scope(self):
        # add on new sub scope
        self.scope.append([])

        # update table
        self.table = self.update_scope(self.table)

        # enter the new scope
        self.scope = self.scope[self.pos]
        # add previous position to scope path
        self.scope_path.append(self.pos)
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
                return self.scope

        # call with global table
        self.table = update_table(self.table)
        # remove layer from scope path
        self.scope_path.pop()

    # add variable to symbol table
    def add_variable(self, sym, ast):
        # compile symbol from action tree Identifier
        if sym.name in [x.name for x in self.scope if isinstance(x, Symbol)]:
            # throw error
            errormodule.throw('semantic_error', 'Variable \'%s\' redeclared.' % sym.name, ast)
        self.scope.append(sym)
        # update table
        self.table = self.update_scope(self.table)
        # add to pos
        self.pos += 1

    # add package to symbol table
    # NOTE packages content is expected to be IR Object
    def add_package(self, pkg):
        # if the package is used, add raw include table to it
        # if pkg.used:
        #     self.scope += self.remove_externals(pkg.content.symbol_table.table)
        # else:
        #     # neither symbol has groups, name is name, data_type is PACKAGE with no pointers, and members is package IR Object
        #
        #     # if it is external, give symbol external modifier
        #     if pkg.is_external:
        #         sym = Symbol(pkg.name, [], types.DataType(types.DataTypes.PACKAGE, []), [Modifiers.EXTERNAL], pkg.content)
        #     else:
        #         sym = Symbol(pkg.name, [], types.DataType(types.DataTypes.PACKAGE, []), [], pkg.content)
        #     self.scope.append(sym)
        pass

    # find symbol in table
    def look_up(self, var):
        # list that holds all visible layers
        layers = list()
        # holds the current layer being appended to layers
        c_layer = self.table
        # follow scope path to get all viable layers
        for item in self.scope_path:
            layers.append(c_layer)
            # updated c_layer
            c_layer = c_layer[item]
        # add current scope to layers (not added before)
        layers.append(self.scope)
        # iterate through layers INWARDS to OUTWARDS (allow for shadowing)
        for layer in reversed(layers):
            for item in layer:
                # handle non packages
                if isinstance(item, Symbol):
                    if item.compare(var) and Modifiers.DELETED not in item.modifiers:
                        # if the symbols are relatively equal, return Symbol
                        return item
                # handle packages
                elif isinstance(item, Package):
                    if item.name == var:
                        return item
        # return nothing if unable to match

    # delete a symbol (give it the delete modifier)
    def delete(self, var):
        deleted = False

        def delete(layer):
            nonlocal deleted
            for i in range(len(layer)):
                if isinstance(layer[i], list):
                    layer[i] = delete(layer[i])
            # if it has not been caught in previous layers
            if not deleted:
                for i in range(len(layer)):
                    if isinstance(layer[i], Symbol) and layer[i].compare(var):
                        layer[i].modifiers.append(Modifiers.DELETED)
                        deleted = True
                        return layer
            return layer
        # attempt to delete symbol
        self.table = delete(self.table)
        # return false if unable to delete
        return deleted

    # remove external modifiers from imported symbol table
    def remove_externals(self, table):
        # iterate through upper table
        for i in range(len(table)):
            # temporary constant to store table item
            item = table[i]
            # if it is a symbol, remove from the table if it is not external
            if isinstance(item, Symbol):
                if Modifiers.EXTERNAL not in item.modifiers:
                    table.pop(i)
                # if it is external, remove the external modifier so it is external to other import layers
                else:
                    table[i].modifiers.pop(table[i].modifiers.index(Modifiers.EXTERNAL))
            else:
                # if there are sub tables, bring the externals in those to the surface
                table[i:i] = self.raise_externals(table[i])
        return table

    # get all external symbols from non surface layers
    def raise_externals(self, sub_scope):
        # temporary list to hold all externals being brought up from lower layers
        externals = []
        for item in sub_scope:
            # if item is symbol, add the symbol with the external modifier removed to externals
            if isinstance(item, Symbol):
                if Modifiers.EXTERNAL in item.modifiers:
                    item.modifiers.pop(item.modifiers.index(Modifiers.EXTERNAL))
                    externals.append(item)
            else:
                # recur and extend externals
                externals += self.raise_externals(item)
        # return temporary list back as externals set
        return externals

