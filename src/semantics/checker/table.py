class TableManager:
    def __init__(self, table):
        self.table = table
        self.level = table
        self.current = None
        self.pos = 0
        self.prevPos = []
        self.layers = []

    def update(self):
        self.pos += 1

    def find(self, elem):
        pass

    def descend(self):
        self.layers.append(self.level)
        self.level = self.level[self.pos + 1]
        self.pos = 0
        self.prevPos.append(self.pos)

    def ascend(self):
        self.level = self.layers.pop()
        self.pos = self.prevPos[-1]