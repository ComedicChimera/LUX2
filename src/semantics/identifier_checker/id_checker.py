from src.parser.ASTtools import ASTNode


class TableManager:
    def __init__(self, table):
        self.table = table
        self.scope = 0
        self.level = table
        self.current = None
        self.pos = 0
        self.prevPos = []

    def update(self):
        self.pos += 1

    def find(self, elem):
        pass

    def descend(self):
        self.scope += 1
        self.level = self.level[self.pos + 1]
        self.pos = 0
        self.prevPos.append(self.pos)

    def ascend(self):
        self.scope -= 1
        # navigate to previous level
        self.pos = self.prevPos[-1]

tb = None


def check(ast):
    for item in ast.content:
        if isinstance(item, ASTNode):
            # no params
            if item.name in ["struct_block", "interface_block", "type_block", "module_block"]:
                tb.update()
            # var
            elif item.name == "variable_declaration":
                # check expr
                tb.update()
            # function
            elif item.name in ["func_block", "constructor_block"]:
                # special check function
                tb.update()
            elif item.name == "block":
                tb.descend()
                check(ast)
                tb.ascend()
            else:
                check(ast)


def check_id(table, ast):
    global tb
    tb = TableManager(table)
    del table
    check(ast)
