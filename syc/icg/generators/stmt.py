from syc.icg.generators.expr import generate_expr
from syc.icg.generators.data_types import generate_type
from syc.ast.ast import ASTNode, unparse
import errormodule
from syc.icg.action_tree import ExprNode, Identifier, StatementNode
import util
from syc.icg.table import Symbol, Modifiers
import syc.icg.types as types
from syc.icg.modules import get_instance
from syc.icg.constexpr import check as check_constexpr


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
        'break_stmt': lambda s, a: StatementNode('Break') if context.break_context else errormodule.throw('semantic_error', 'Invalid context for break statement',
                                                                                                           stmt),
        'continue_stmt': lambda s, a: StatementNode('Continue') if context.continue_context else errormodule.throw('semantic_error', 'Invalid context for continue statement',
                                                                                                                    stmt),
        'throw_stmt': lambda s: StatementNode('Throw', generate_expr(s.content[1])),
        'variable_declaration': lambda s: generate_variable_declaration(s, []),
        'external_stmt': lambda s: generate_variable_declaration(s.content[1].content[0], [Modifiers.EXTERNAL]),
        'volatile_stmt': lambda s: generate_variable_declaration(s.content[-1], [Modifiers.VOLATILE] if s.content[1].name != 'extern' else [Modifiers.VOLATILE,
                                                                                                                                            Modifiers.EXTERNAL]),
        'assignment': generate_assignment,
        'delete_stmt': generate_delete
    }[stmt.name](*([stmt, context] if stmt.name in {'yield_stmt', 'return_stmt', 'break_stmt', 'continue_stmt'} else [stmt]))


# prevent recursive imports
from syc.icg.generators.atom import add_trailer


# generate a return value for both returns and generators
def generate_return(stmt, context):
    if context.return_context:
        return StatementNode('Return' if stmt.name == 'return_stmt' else 'Yield', generate_expr(stmt.content[1]))
    else:
        errormodule.throw('semantic_error', 'Invalid context for ' + ('yield statement' if stmt.name == 'yield_stmt' else 'return statement'), stmt)


def generate_delete(stmt):
    identifiers = []
    variables = [stmt.content[1]]
    if isinstance(stmt.content[-1], ASTNode):
        for item in unparse(stmt.content[-1]):
            if item.type == 'IDENTIFIER':
                variables.append(item)
    for item in variables:
        sym = util.symbol_table.look_up(item.value)
        if not util.symbol_table.delete(item.value):
            errormodule.throw('semantic_error', 'Unable to delete non-existent symbol', item)
        identifiers.append(Identifier(sym.name, sym.data_type, Modifiers.CONSTANT in sym.modifiers))
    return StatementNode('Delete', *identifiers)


# create and evaluate a variable declaration
def generate_variable_declaration(stmt, modifiers):
    constant = False
    variables = {}
    overall_type = None
    initializer = None
    constexpr = False
    # iterate to generate statement components
    for item in stmt.content:
        if isinstance(item, ASTNode):
            if item.name == 'var':
                variables = generate_var(item)
            elif item.name == 'extension':
                overall_type = generate_type(item.content[1])
            elif item.name == 'initializer':
                initializer = generate_expr(item.content[1])
                constexpr = item.content[0].type == ':='
        elif item.type == '@':
            constant = True
    if constant:
        modifiers.append(Modifiers.CONSTANT)
    if constexpr and not constant:
        errormodule.throw('semantic_error', 'Declaration of constexpr on non-constant', stmt)
    if isinstance(variables, dict):
        # if any variable has initializer
        has_init = False
        for k, v in variables.items():
            if v.constexpr and not constant:
                errormodule.throw('semantic_error', 'Declaration of constexpr on non-constant', stmt)
            val = None
            if hasattr(v, 'initializer'):
                has_init = True
            if v.constexpr:
                val = v.initializer
            sym = Symbol(k.value, v.data_type if hasattr(v, 'data_type') else overall_type, modifiers + [Modifiers.CONSTEXPR] if v.constexpr else modifiers, value=val)
            if not sym.data_type:
                errormodule.throw('semantic_error', 'Unable to infer data type of variable', k)
            elif not overall_type and isinstance(sym.data_type, types.DataType) and sym.data_type.data_type == types.DataTypes.NULL:
                errormodule.throw('semantic_error', 'Unable to infer data type of variable', k)
            util.symbol_table.add_variable(sym, k)
        if initializer:
            if has_init:
                errormodule.throw('semantic_error', '%s cannot have two initializers' % ('constant' if constant else 'variable'), stmt)
            if isinstance(initializer.data_type, types.Tuple):
                pass
        return StatementNode('DeclareConstants' if constant else 'DeclareVariables', overall_type, dict(zip([k.value for k in variables.keys()], variables.values())), modifiers)
    else:
        if not overall_type and not initializer:
            errormodule.throw('semantic_error', 'Unable to infer data type of variable', stmt)
        if not overall_type and isinstance(initializer.data_type, types.DataType) and initializer.data_type.data_type == types.DataTypes.NULL:
            errormodule.throw('semantic_error', 'Unable to infer data type of variable', stmt)
        if overall_type and not types.coerce(overall_type, initializer.data_type):
            errormodule.throw('semantic_error', 'Variable type extension and initializer data types do not match', stmt)
        if constexpr:
            modifiers.append(Modifiers.CONSTEXPR)
            # assume initializer exists
            check_constexpr(initializer, stmt)
        util.symbol_table.add_variable(Symbol(variables.value, overall_type, modifiers, None if not constexpr else initializer), stmt)
        return StatementNode('DeclareConstant' if constant else 'DeclareVariable', overall_type, variables.value, initializer, modifiers)


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
                    if not types.coerce(final_variable['data_type'], variable['initializer'].data_type):
                        errormodule.throw('semantic_error', 'Variable type extension and initializer data types do not match', variable['name'])
                else:
                    final_variable['data_type'] = variable['initializer'].data_type
                final_variable['initializer'] = variable['initializer']
                final_variable['constexpr'] = variable['constexpr']
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
                        variable['constexpr'] = item.content[0].type == ':='
                        if variable['constexpr']:
                            check_constexpr(variable['initializer'], item.content[-1])
                    elif item.name == 'multi_var':
                        add_final_variable()
                        generate_variable_dict(item)
                elif item.type == 'IDENTIFIER':
                    variable['name'] = item

        generate_variable_dict(var_ast)
        add_final_variable()

        return variables


def generate_assignment(assignment):
    await, new, root = False, False, None
    for item in assignment.content:
        if item.name == 'await':
            await = True
        elif item.name == 'new':
            new = True
        elif item.name == 'assign_var':
            root = generate_assign_var(item)
        elif item.name == 'trailer':
            root = add_trailer(root, item)
        elif item.name == 'assignment_expr':
            if await or new:
                errormodule.throw('semantic_error', 'Invalid operands for %s operator' % 'await' if await else 'new', item)
            root = generate_assignment_expr(root, item)
    if await:
        if not isinstance(root.data_type, types.IncompleteType):
            errormodule.throw('semantic_error', 'Unable to await object', assignment)
        root = StatementNode('Expr', ExprNode('Await', root.data_type.data_type, root))
    if new:
        pass
    return root


def generate_assign_var(assign_var):
    def generate_id_type(id_type):
        if id_type.content[0].type == 'THIS':
            return get_instance()
        else:
            sym = util.symbol_table.look_up(id_type.content[0].value)
            if not sym:
                errormodule.throw('semantic_error', 'Variable \'%s\' not defined' % id_type.content[0].value, id_type)
            return Identifier(sym.name, sym.data_type, Modifiers.CONSTANT in sym.modifiers)

    if isinstance(assign_var.content[0], ASTNode):
        return generate_id_type(assign_var.content[0])
    else:
        if isinstance(assign_var.content[-1].content[0], ASTNode):
            root = generate_id_type(assign_var.content[-1].content[0])
        else:
            root = generate_assign_var(assign_var.content[-1].content[1])
            if len(assign_var.content[-1].content) > 3:
                root = add_trailer(root, assign_var.content[-1].content[2])
        deref_count = 1 if len(assign_var.content) == 2 else len(unparse(assign_var.content[1])) + 1
        if deref_count != root.data_type.pointers:
            errormodule.throw('semantic_error', 'Unable to dereference a non-pointers', assign_var)
        return ExprNode('Dereference', None, deref_count, root)


def generate_assignment_expr(root, assign_expr):
    if isinstance(assign_expr.content[0], ASTNode):
        is_n_assign = int(assign_expr.content[0].name != 'n_assignment')
        variables, initializers = [root], [generate_expr(assign_expr.content[2 - is_n_assign])]
        if assign_expr.content[0].name == 'n_assignment':
            assign_content = assign_expr.content[0].content
            for item in assign_content:
                if isinstance(item, ASTNode):
                    if item.name == 'assign_var':
                        variables.append(generate_assign_var(item))
                    elif item.name == 'n_assignment':
                        assign_content = item.content
        if assign_expr.content[-1].name == 'n_list':
            expressions = assign_expr.content[-1].content
            for item in expressions:
                if isinstance(item, ASTNode):
                    if item.name == 'expr':
                        expr = generate_expr(item)
                        if isinstance(expr.data_type, types.Tuple):
                            for elem in expr.data_type.values:
                                initializers.append(elem)
                        else:
                            initializers.append(expr)
                    elif item.name == 'n_list':
                        expressions = item.content
        if len(variables) != len(initializers):
            errormodule.throw('semantic_error', 'Assignment value counts don\'t match', assign_expr)
        op = assign_expr.content[1 - is_n_assign].content[0]
        for var, expr in zip(variables, initializers):
            if not modifiable(var):
                errormodule.throw('semantic_error', 'Unable to modify unmodifiable l-value', assign_expr)
            if not types.coerce(var.data_type, expr.data_type):
                errormodule.throw('semantic_error', 'Variable type and reassignment type do not match', assign_expr)
            if op.type != '=':
                if not types.numeric(var.data_type):
                    errormodule.throw('semantic_error', 'Compound assignment operator invalid for non-numeric type', op)
        return StatementNode('Assign', op.type, dict(zip(variables, initializers)))
    else:
        if not modifiable(root):
            errormodule.throw('semantic_error', 'Unable to modify unmodifiable l-value', assign_expr)
        if not types.numeric(root.data_type):
            errormodule.throw('semantic_error', 'Unable to increment/decrement non numeric value', assign_expr)
        if assign_expr.content[0].type == '+':
            root = StatementNode('Increment', root)
        else:
            root = StatementNode('Decrement', root)
    return root


def modifiable(root):
    if isinstance(root, Identifier):
        return not root.constant
    for item in root.arguments:
        pass
    return True
