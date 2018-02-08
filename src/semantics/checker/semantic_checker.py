import src.semantics.checker.table as table_util
from src.semantics.checker.infer import infer


def check(ast, table):
    table_util.tm = table_util.TableManager(table)
    infer(table)
