from src.semantics.semantics import DataStructure
from src.semantics.symbols.symbol_table import Package
import pickle
from src.parser.ASTtools import ASTNode


# table manager - controls table for analysis
class TableManager:
    def __init__(self, table):
        self.table = table
        self.pos = 0
        self.prevPos = []

    def find(self, elem):
        layers = self.prevPos
        level = self.table
        while True:
            top = False
            for item in layers:
                level = level[item]
            if level == self.table:
                top = True
            for var in level:
                if isinstance(var, Package):
                    if var.used:
                        pass
                    elif var.alias == elem.name:
                        return self.unpack(var).find(elem)
                if self.compare(var, elem):
                    return var
            else:
                if top:
                    return False
                layers.pop()

    @staticmethod
    def unpack(pkg):
        table = pickle.load(pkg.dep_dir).symbol_table

        class OpenedPackage:
            def __init__(self):
                self.visible = []
                self.available_packages = []
                for item in table:
                    if isinstance(item, ASTNode):
                        if has_modifier(item, "GLOBAL"):
                            self.visible.append(item)
                    elif isinstance(item, Package):
                        if item.is_global:
                            self.available_packages.append(item)
                self.is_global = pkg.is_global
                self.used = pkg.used

            def find(self, elem):
                if not self.used:
                    elem.group = elem.group[1:]
                for pkg in self.available_packages:
                    res = TableManager.unpack(pkg).find(elem)
                    if res:
                        return res
                for item in self.visible:
                    if TableManager.compare(item, elem):
                        return item
                    else:
                        return False

        return OpenedPackage()

    # compares identifier w/ member from table
    @staticmethod
    def compare(var1, var2):
        def raw_compare(val1=var1, val2=var2):
            if val1.name == val2.name and val1.group == val2.group and val1.is_instance == val2.is_instance:
                return True

        if raw_compare():
            return True
        if var2.data_structure in [DataStructure.STRUCT, DataStructure.INTERFACE, DataStructure.TYPE, DataStructure.MODULE]:
            for item in var2.members:
                if raw_compare(var1, item):
                    return True
        return False

    def descend(self):
        self.prevPos.append(self.pos)
        self.pos = 0

    def ascend(self):
        self.pos = self.prevPos[-1]

    def reset(self):
        self.pos = 0
        self.prevPos = []

    def update(self):
        self.pos += 1


def has_modifier(name, var):
    pass

tm = None

