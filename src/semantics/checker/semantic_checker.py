import src.semantics.checker.table as table_util
from src.semantics.checker.expr_checker import parse


def check(ast, table):
    table_util.tm = table_util.TableManager(table)
    infer(table)


def infer(table):
    for item in table:
        if isinstance(item, list):
            table_util.tm.descend()
            infer(item)
            table_util.tm.ascend()
        else:
            table_util.tm.update()
            if item.data_type == "INFER":
                item.data_type = parse(item)
    table_util.tm.reset()
