from syc.icg.generators.expr import generate_expr
from syc.icg.generators.data_types import generate_type
from syc.parser.ASTtools import ASTNode
import errormodule
from syc.icg.action_tree import ActionNode
import util
from syc.icg.table import Symbol, Modifiers
import syc.icg.types as types


class Context:
    def __init__(self, br, cn, rt):
        self.return_context = rt
        self.continue_context = cn
        self.break_context = br


# statement generator function
def generate_statement(stmt, context: Context):
    return {
        'return_stmt': generate_return,
        'yield_stmt': generate_return,
        'break_stmt': lambda s, a: ActionNode('Break', None) if context.break_context else errormodule.throw('semantic_error', 'Invalid context for break statement',
                                                                                                             stmt),
        'continue_stmt': lambda s, a: ActionNode('Continue', None) if context.continue_context else errormodule.throw('semantic_error', 'Invalid context for continue statement',
                                                                                                                      stmt),
        'throw_stmt': lambda s: ActionNode('Throw', None, generate_expr(s.content[1])),
        'variable_declaration': lambda s: generate_variable_declaration(s, []),
        'external_stmt': lambda s: generate_variable_declaration(s.content[1].content[0], [Modifiers.EXTERNAL]),
        'volatile_stmt': lambda s: generate_variable_declaration(s.content[-1], [Modifiers.VOLATILE] if s.content[1].name != 'extern' else [Modifiers.VOLATILE,
                                                                                                                                            Modifiers.EXTERNAL]),
        'assignment': generate_assignment
    }[stmt.name](*([stmt, context] if stmt.name in {'yield_stmt', 'return_stmt', 'break_stmt', 'continue_stmt'} else [stmt]))


# generate a return value for both returns and generators
def generate_return(stmt, context):
    if context.return_context:
        return ActionNode('Return' if stmt.name == 'return_stmt' else 'Yield', None, generate_expr(stmt.content[1]))
    else:
        errormodule.throw('semantic_error', 'Invalid context for ' + ('yield statement' if stmt.name == 'yield_stmt' else 'return statement'), stmt)


# create and evaluate a variable declaration
def generate_variable_declaration(stmt, modifiers):
    constant = False
    variables = {}
    overall_type = None
    initializer = None
    # iterate to generate statement components
    for item in stmt.content:
        if isinstance(item, ASTNode):
            if item.name == 'var':
                variables = generate_var(item)
            elif item.name == 'extension':
                overall_type = generate_type(item.content[1])
            elif item.name == 'initializer':
                initializer = generate_expr(item.content[1])
        elif item.type == '@':
            constant = True
    if isinstance(variables, dict):
        for k, v in variables.items():
            sym = Symbol(k.value, v.data_type if hasattr(v, 'data_type') else overall_type, [Modifiers.CONSTANT] + modifiers if constant else modifiers)
            if not sym.data_type:
                errormodule.throw('semantic_error', 'Unable to infer data type of variable', k)
            util.symbol_table.add_variable(sym, k)
        if initializer:
            errormodule.throw('semantic_error', 'Multi-%s declaration cannot have global initializer' % ('constant' if constant else 'variable'), stmt)
        return ActionNode('DeclareConstants' if constant else 'DeclareVariables', overall_type, dict(zip([k.value for k in variables.keys()], variables.values())), modifiers)
    else:
        if not overall_type and not initializer:
            errormodule.throw('semantic_error', 'Unable to infer data type of variable', stmt)
        if not types.dominant(overall_type, initializer.data_type):
            errormodule.throw('semantic_error', 'Variable type extension and initializer data types do not match', stmt)
        util.symbol_table.add_variable(Symbol(variables.value, overall_type, [Modifiers.CONSTANT] + modifiers if constant else modifiers), stmt)
        return ActionNode('DeclareConstant' if constant else 'DeclareVariable', overall_type, variables.value, initializer, modifiers)


# generate var (from AST in variable declaration)
def generate_var(var_ast):
    if var_ast.content[0].type == 'IDENTIFIER':
        return var_ast.content[0]
    else:
        def add_final_variable():
            final_variable = {}
            if 'extension' in variable:
                final_variable['data_type'] = variable['extension']
            if 'initializer' in variable:
                if 'data_type' in final_variable:
                    if not types.dominant(final_variable['data_type'], variable['initializer'].data_type):
                        errormodule.throw('semantic_error', 'Variable type extension and initializer data types do not match', variable['name'])
                else:
                    final_variable['data_type'] = variable['initializer'].data_type
                final_variable['initializer'] = variable['initializer']
            variables[variable['name']] = type('Object', (), final_variable)

        variables = {}
        variable = {}

        def generate_variable_dict(ast):
            for item in ast.content:
                if isinstance(item, ASTNode):
                    if item.name == 'extension':
                        variable['extension'] = generate_type(item.content[-1])
                    elif item.name == 'initializer':
                        variable['initializer'] = generate_expr(item.content[-1])
                    elif item.name == 'multi_var':
                        add_final_variable()
                        generate_variable_dict(item)
                elif item.type == 'IDENTIFIER':
                    variable['name'] = item

        generate_variable_dict(var_ast)
        add_final_variable()

        return variables


def generate_assignment(assignment):
    pass