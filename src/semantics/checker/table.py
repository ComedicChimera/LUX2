from src.semantics.semantics import DataStructure


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
                if self.compare(var, elem):
                    return var
            else:
                if top:
                    return False
                layers.pop()

    # compares identifier w/ member from table
    @staticmethod
    def compare(var1, var2):
        def raw_compare(var1=var1, var2=var2):
            if var1.name == var2.name and var1.group == var2.group and var1.is_instance == var2.is_instance:
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

