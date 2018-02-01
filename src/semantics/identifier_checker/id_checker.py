from src.parser.ASTtools import ASTNode
from src.errormodule import throw


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


def check_expr(expr):
    pass


def check(ast):
    for item in ast.content:
        if isinstance(item, ASTNode):
            # no params
            if item.name in ["struct_block", "interface_block", "type_block", "module_block"]:
                tb.update()
            # var
            elif item.name == "variable_declaration":
                tb.update()
                check_expr(tb.level[tb.pos].initializer)
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


def catch_repeats(table):
    used_names = []
    for item in table:
        if isinstance(item, list):
            catch_repeats(item)
        else:
            identifier = [item.name, item.group, item.is_instance]
            if identifier in used_names:
                # get id pos
                throw("semantic_error", "Variable declared multiple times.", identifier[0])
            used_names.append(identifier)


def check_id(table, ast):
    global tb
    tb = TableManager(table)
    del table
    check(ast)
