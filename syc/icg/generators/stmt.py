from syc.icg.generators.expr import generate_expr
from syc.parser.ASTtools import ASTNode
import errormodule
from syc.icg.action_tree import ActionNode


class Context:
    def __init__(self, br, cn, rt):
        self.return_context = rt
        self.continue_context = cn
        self.break_context = br


# statement generator function
def generate_statement(stmt, context: Context):
    # remove includes from generation (already evaluated)
    if stmt.name == 'include':
        return
    return {
        'return_stmt': generate_return,
        'yield_stmt': generate_return,
        'break_stmt': lambda s, a: ActionNode('Break', None) if context.break_context else errormodule.throw('semantic_error', 'Invalid context for break statement',
                                                                                                             stmt),
        'continue_stmt': lambda s, a: ActionNode('Continue', None) if context.continue_context else errormodule.throw('semantic_error', 'Invalid context for continue statement',
                                                                                                                      stmt),
        'throw_stmt': lambda s: ActionNode('Throw', None, generate_expr(s.content[1]))
    }[stmt.name](*([stmt, context] if stmt.name in {'yield_stmt', 'return_stmt', 'break_stmt', 'continue_stmt'} else [stmt]))


def generate_return(stmt, context):
    if context.return_context:
        return ActionNode('Return' if stmt.name == 'return_stmt' else 'Yield', None, generate_expr(stmt.content[1]))
    else:
        errormodule.throw('semantic_error', 'Invalid context for ' + ('yield statement' if stmt.name == 'yield_stmt' else 'return statement'), stmt)