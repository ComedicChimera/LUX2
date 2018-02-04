import src.semantics.checker.table as table_util


def check(ast, table):
    tm = table_util.TableManager(table)
