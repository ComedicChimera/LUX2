class TableManager:
    def __init__(self, table):
        self.table = table
        self.scope = 0
        self.level = table
        self.current = None

    def update(self, elem):
        pass

    def find(self, elem):
        pass


def check_id(table, ast):
    tb = TableManager(table)
    del table
