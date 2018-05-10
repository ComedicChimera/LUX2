from syc.icg.table import SymbolTable
from syc.parser.ASTtools import ASTNode
import util
from syc.icg.generators.expr import generate_expr


def generate_tree(ast):
    util.symbol_table = SymbolTable()
    for item in ast.content:
        if isinstance(item, ASTNode):
            # test code for expr compiler
            if item.name == 'expr':
                try:
                    print(generate_expr(item))
                except util.SyCloneRecoverableError as e:
                    print(str(e) + '\n')
            else:
                generate_tree(item)
        elif isinstance(item, util.Package):
            # store working table to restore after completion
            local_table = util.symbol_table
            # generate new package element
            local_tree = generate_tree(item.content)
            # create new package content object
            # util.symbol_table being the package's working table
            item.content = type('Object', (), dict(symbol_table=util.symbol_table, action_tree=local_tree))
            # reset symbol table
            util.symbol_table = local_table
            util.symbol_table.add_package(item)
    return ast
