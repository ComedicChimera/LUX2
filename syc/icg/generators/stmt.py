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
from copy import copy


# context to hold where statements are valid
class Context:
    def __init__(self, br, cn, rt):
        self.return_context = rt
        self.continue_context = cn
        self.break_context = br


# statement generator function
def generate_statement(stmt, context: Context):
    return {
        # handle return
        'return_stmt': generate_return,
        # handle yield
        # yield uses same function, b/c it differentiates
        'yield_stmt': generate_return,
        # generate break statement and check context
        'break_stmt': lambda s, a: StatementNode('Break') if context.break_context else errormodule.throw('semantic_error', 'Invalid context for break statement',
                                                                                                           stmt),
        # generate continue statement and check context
        'continue_stmt': lambda s, a: StatementNode('Continue') if context.continue_context else errormodule.throw('semantic_error', 'Invalid context for continue statement',
                                                                                                                    stmt),
        # generate throw statement
        'throw_stmt': lambda s: StatementNode('Throw', generate_expr(s.content[1])),
        # generate variable with no modifiers
        'variable_declaration': lambda s: generate_variable_declaration(s, []),
        # generate variable with external modifier
        'external_stmt': lambda s: generate_variable_declaration(s.content[1].content[0], [Modifiers.EXTERNAL]),
        # generate variable with volatile and possibly external modifiers
        'lock_stmt': lambda s: generate_variable_declaration(s.content[-1], [Modifiers.LOCK] if s.content[1].name != 'extern' else [Modifiers.LOCK,
                                                                                                                                        Modifiers.EXTERNAL]),
        # generate assignment / function call statement
        'assignment': generate_assignment,
        # generate delete statement
        'delete_stmt': generate_delete
    # subscript to get statement name and then call function, pass in context if necessary
    }[stmt.name](*([stmt, context] if stmt.name in {'yield_stmt', 'return_stmt', 'break_stmt', 'continue_stmt'} else [stmt]))


# prevent recursive imports
from syc.icg.generators.atom import add_trailer


# generate a return value for both returns and generators
def generate_return(stmt, context):
    # generate return or yield if possible
    if context.return_context:
        return StatementNode('Return' if stmt.name == 'return_stmt' else 'Yield', generate_expr(stmt.content[1]))
    else:
        errormodule.throw('semantic_error', 'Invalid context for ' + ('yield statement' if stmt.name == 'yield_stmt' else 'return statement'), stmt)


# generate and check delete statement
def generate_delete(stmt):
    # hold Identifiers to be put in final StatementNode
    identifiers = []
    # hold the initial variable names given
    variables = [stmt.content[1]]
    # if there are multiple variables
    if isinstance(stmt.content[-1], ASTNode):
        # iterate through unparsed statement and add all identifiers
        for item in unparse(stmt.content[-1]):
            if item.type == 'IDENTIFIER':
                variables.append(item)
    # iterate through generated variable list
    for item in variables:
        # look up to get identifier
        sym = util.symbol_table.look_up(item.value)
        # attempt to delete, fail if impossible
        if not util.symbol_table.delete(item.value):
            errormodule.throw('semantic_error', 'Unable to delete non-existent symbol', item)
        # add identifiers to list
        identifiers.append(Identifier(sym.name, sym.data_type, Modifiers.CONSTANT in sym.modifiers))
    return StatementNode('Delete', *identifiers)


# create and evaluate a variable declaration
def generate_variable_declaration(stmt, modifiers):
    # is constant
    constant = False
    # for multideclaration: holds set of variables
    variables = {}
    # main type extension
    overall_type = None
    # main variable initializer
    initializer = None
    # is marked constexpr
    constexpr = False
    # iterate to generate statement components
    for item in stmt.content:
        if isinstance(item, ASTNode):
            # generate variable if name given
            if item.name == 'var':
                variables = generate_var(item)
            # set overall type
            elif item.name == 'extension':
                overall_type = generate_type(item.content[1])
            # add initializer
            elif item.name == 'initializer':
                initializer = generate_expr(item.content[1])
                # set constexpr if := operator used
                constexpr = item.content[0].type == ':='
        # set constant if @ operator used instead of $
        elif item.type == '@':
            constant = True
    # add constant to modifiers if variable is marked constant
    if constant:
        modifiers.append(Modifiers.CONSTANT)
    # all constexpr variables must also be constant
    if constexpr and not constant:
        errormodule.throw('semantic_error', 'Declaration of constexpr on non-constant', stmt)
    # if multi-declaration was used
    if isinstance(variables, dict):
        # position in variable set
        pos = 0
        # iterate through variable dictionary
        # k = identifier token, v = generated variable object
        for k, v in variables.items():
            # handle variables marked constexpr in non constant environment
            if v.constexpr and not constant:
                errormodule.throw('semantic_error', 'Declaration of constexpr on non-constant', stmt)
            # if there is a global initializer
            if initializer:
                # if it is tuple based initializer
                if isinstance(initializer.data_type, types.Tuple):
                    # if the variable is still within the domain of the global initializer
                    if pos < len(initializer.data_type.values):
                        # if is doesn't have a data type, add the one provided by the initializer
                        if not hasattr(v, 'data_type'):
                            setattr(v, 'data_type', initializer.data_type.values[pos].data_type)
                        # handle invalid double initializers, ie $(x = 2, y) = tupleFunc();
                        elif hasattr(v, 'initializer'):
                            errormodule.throw('semantic_error', '%s cannot have two initializers' % ('constant' if constant else 'variable'), k)
                        # if there is a type mismatch between the type extension and the given initializer value
                        elif not types.coerce(v.data_type, initializer.data_type.values[pos].data_type):
                            errormodule.throw('semantic_error', 'Variable type extension and initializer data types do not match', k)
                # otherwise, it is invalid
                else:
                    errormodule.throw('semantic_error', 'Multi-%s declaration cannot have single global initializer' % ('constant' if constant else 'variable'), stmt)
            # constexpr value (constexpr(s) store value so they can be evaluated at compile-time)
            val = None
            if v.constexpr:
                val = v.initializer
            # generate symbol object
            # identifier name, data type, modifiers, value (if constexpr)
            sym = Symbol(k.value, v.data_type if hasattr(v, 'data_type') else overall_type, modifiers + [Modifiers.CONSTEXPR] if v.constexpr else modifiers, value=val)
            # if the symbol lacks a data type
            if not sym.data_type:
                errormodule.throw('semantic_error', 'Unable to infer data type of variable', k)
            # if there is a null declared variable (x = null)
            elif not overall_type and isinstance(sym.data_type, types.DataType) and sym.data_type.data_type == types.DataTypes.NULL:
                errormodule.throw('semantic_error', 'Unable to infer data type of variable', k)
            # add variable to symbol table
            util.symbol_table.add_variable(sym, k)
            pos += 1
        # statement name
        name = 'DeclareConstants' if constant else 'DeclareVariables'
        # if there is an initializer, add it to final statement
        if initializer:
            return StatementNode(name, overall_type, dict(zip([k.value for k in variables.keys()], variables.values())), modifiers, initializer)
        return StatementNode(name, overall_type, dict(zip([k.value for k in variables.keys()], variables.values())), modifiers)
    # if only normal declaration was used
    else:
        # handle null declarations (no type extension or initializer)
        if not overall_type and not initializer:
            errormodule.throw('semantic_error', 'Unable to infer data type of variable', stmt)
        # handle null declarations (no type extension and null initializer)
        if not overall_type and isinstance(initializer.data_type, types.DataType) and initializer.data_type.data_type == types.DataTypes.NULL:
            errormodule.throw('semantic_error', 'Unable to infer data type of variable', stmt)
        # check for type extension and initializer mismatch
        if overall_type and initializer and not types.coerce(overall_type, initializer.data_type):
            errormodule.throw('semantic_error', 'Variable type extension and initializer data types do not match', stmt)
        # add constexpr if marked as such
        if constexpr:
            modifiers.append(Modifiers.CONSTEXPR)
            # assume initializer exists
            if not check_constexpr(initializer):
                errormodule.throw('semantic_error', 'Expected constexpr', stmt)
        # add to symbol table
        util.symbol_table.add_variable(Symbol(variables.value, overall_type if overall_type else initializer.data_type, modifiers, None if not constexpr else initializer), stmt)
        # return generated statement node
        return StatementNode('DeclareConstant' if constant else 'DeclareVariable', overall_type, variables.value, initializer, modifiers)


# generate var (from AST in variable declaration)
def generate_var(var_ast):
    # if it is just a single variable
    if var_ast.content[0].type == 'IDENTIFIER':
        return var_ast.content[0]
    # if it is multi-declaration
    else:
        # create the final variable to be added to variables from variable dictionary (pseudo-object)
        def add_final_variable():
            # holding dictionary
            final_variable = {}
            # add extension if it exists
            if 'extension' in variable:
                final_variable['data_type'] = variable['extension']
            # if the variable has an initializer
            if 'initializer' in variable:
                # if it has a data type, type check the initializer
                if 'data_type' in final_variable:
                    if not types.coerce(final_variable['data_type'], variable['initializer'].data_type):
                        errormodule.throw('semantic_error', 'Variable type extension and initializer data types do not match', variable['name'])
                else:
                    # else infer from initializer
                    final_variable['data_type'] = variable['initializer'].data_type
                # add initializer to variable
                final_variable['initializer'] = variable['initializer']
                # add constexpr designation
                final_variable['constexpr'] = variable['constexpr']
            # add synthesized object to variables
            variables[variable['name']] = type('Object', (), final_variable)

        # hold dictionary of variables
        # keys = names, values = variable objects
        variables = {}
        # current working variable
        variable = {}

        # generate variables from ast
        def generate_variable_dict(ast):
            for item in ast.content:
                # if is an AST
                if isinstance(item, ASTNode):
                    # add extension
                    if item.name == 'extension':
                        variable['extension'] = generate_type(item.content[-1])
                    # add initializer and constexpr
                    elif item.name == 'initializer':
                        variable['initializer'] = generate_expr(item.content[-1])
                        # check for constexpr from initializer operator
                        variable['constexpr'] = item.content[0].type == ':='
                        # perform constexpr check if is constexpr
                        if variable['constexpr']:
                            if not check_constexpr(variable['initializer']):
                                errormodule.throw('semantic_error', 'Expected constexpr', item.content[-1])
                    # recur and continue building variable dictionary
                    elif item.name == 'multi_var':
                        add_final_variable()
                        generate_variable_dict(item)
                # otherwise assume token and check if it identifier
                elif item.type == 'IDENTIFIER':
                    variable['name'] = item

        # generate variables
        generate_variable_dict(var_ast)
        # add last uncaught variable
        add_final_variable()

        # return variables dictionary
        return variables


# generate an assignment / function call statement
def generate_assignment(assignment):
    # await = if 'await' is present, same for new, root is root variable
    await, new, root = False, False, None
    for item in assignment.content:
        # NOTE assumes everything is an AST
        # mark await if it is encountered
        if item.name == 'await':
            await = True
        # mark new if it is encounted
        elif item.name == 'new':
            new = True
        # generate the assignment variable if the given AST is encountered
        elif item.name == 'assign_var':
            root = generate_assign_var(item)
        # add trailer if it detected
        elif item.name == 'trailer':
            root = add_trailer(root, item)
        # handle extended assignment expression
        elif item.name == 'assignment_expr':
            # await and new are invalid on assignment
            if await or new:
                errormodule.throw('semantic_error', 'Invalid operands for %s operator' % 'await' if await else 'new', item)
            root = generate_assignment_expr(root, item)
    # check await
    if await:
        # if it is not returning and Incomplete Type, an async function was not called
        if not isinstance(root.data_type, types.Future):
            errormodule.throw('semantic_error', 'Unable to await object', assignment)
        root = StatementNode('Expr', ExprNode('Await', root.data_type.data_type, root))
    # check new
    if new:
        expr = None
        # if it is not a structure of a group
        if root.data_type != types.DataTypes.MODULE:
            # if it is a data type
            if isinstance(root.data_type, types.DataTypeLiteral):
                # get new pointer type
                dt = copy(root.data_type)
                dt.pointers += 1
                # return memory allocation with size of type
                expr = ExprNode('Malloc', dt, ExprNode('SizeOf', types.DataType(types.DataTypes.INT, 1), root))
            else:
                # if it is not an integer
                if root.data_type != types.DataType(types.DataTypes.INT, 0):
                    # all tests failed, not allocatable
                    errormodule.throw('semantic_error', 'Unable to dynamically allocate memory for object', assignment)
                else:
                    # malloc for just int size
                    expr = ExprNode('Malloc', types.VOID_PTR, root)
        else:
            dt = copy(root.data_type)
            dt.instance = True
            # return object instance
            expr = ExprNode('CreateObjectInstance', dt, root)
        root = StatementNode('Expr', expr)
    # return compiled root
    return root


# generate the assignment variable
def generate_assign_var(assign_var):
    # generate identifier
    def generate_id_type(id_type):
        # handle this token
        # uses Module.get_instance()
        if id_type.content[0].type == 'THIS':
            return get_instance()
        # otherwise look up symbol and return identifier
        else:
            sym = util.symbol_table.look_up(id_type.content[0].value)
            if not sym:
                errormodule.throw('semantic_error', 'Variable \'%s\' not defined' % id_type.content[0].value, id_type)
            return Identifier(sym.name, sym.data_type, Modifiers.CONSTANT in sym.modifiers)

    # if there is single ASTNode, assume the it is id_types
    if isinstance(assign_var.content[0], ASTNode):
        # return generate id type
        return generate_id_type(assign_var.content[0])
    # there is a dereference operator
    else:
        # check if there is an id type after the dereference operator
        if isinstance(assign_var.content[-1].content[0], ASTNode):
            root = generate_id_type(assign_var.content[-1].content[0])
        # otherwise generate sub var
        else:
            root = generate_assign_var(assign_var.content[-1].content[1])
            # check for trailer
            if len(assign_var.content[-1].content) > 3:
                root = add_trailer(root, assign_var.content[-1].content[2])
        # calculate the dereference count
        deref_count = 1 if len(assign_var.content) == 2 else len(unparse(assign_var.content[1])) + 1
        # check for non-pointer dereference
        if deref_count > root.data_type.pointers:
            errormodule.throw('semantic_error', 'Unable to dereference a non-pointers', assign_var)
        dt = copy(root.data_type)
        dt.pointers -= deref_count
        return ExprNode('Dereference', dt, deref_count, root)


# generate the remain components of the assignment expression if possible
def generate_assignment_expr(root, assign_expr):
    # check for traditional assignment
    if isinstance(assign_expr.content[0], ASTNode):
        # NOTE all upper level values are ASTNodes
        # value is used to determine where to begin generating assignment expr
        is_n_assign = int(assign_expr.content[0].name != 'n_assignment')
        # variables is the collection of variables used in assignment (assign vars)
        # initializers is the matching initializer set
        variables, initializers = [root], [generate_expr(assign_expr.content[2 - is_n_assign])]
        # if there are multiple variables
        if assign_expr.content[0].name == 'n_assignment':
            # holding content used in recursive for loop
            assign_content = assign_expr.content[0].content
            for item in assign_content:
                # ignore commas
                if isinstance(item, ASTNode):
                    # check for the assignment variable
                    if item.name == 'assign_var':
                        # add generated assignment variable
                        variables.append(generate_assign_var(item))
                    elif item.name == 'n_assignment':
                        # recur
                        assign_content = item.content
        # if there are multiple expressions
        if assign_expr.content[-1].name == 'n_list':
            # holding content used in recursive for loop
            expressions = assign_expr.content[-1].content
            for item in expressions:
                # ignore commas
                if isinstance(item, ASTNode):
                    # check for expression (initializer)
                    if item.name == 'expr':
                        # generate initializer expression
                        expr = generate_expr(item)
                        # if it is a tuple (multiple values stored in a single expression)
                        if isinstance(expr.data_type, types.Tuple):
                            # add each value to expression set (de-tuple)
                            for elem in expr.data_type.values:
                                initializers.append(elem)
                        # else add raw expr to list
                        else:
                            initializers.append(expr)
                    elif item.name == 'n_list':
                        # recur
                        expressions = item.content
        # check for matching assignment properties (unmodified variables)
        if len(variables) != len(initializers):
            errormodule.throw('semantic_error', 'Assignment value counts don\'t match', assign_expr)
        # get the assignment operator used
        # use offset to calculate it
        op = assign_expr.content[1 - is_n_assign].content[0]
        # iterate through variables and initializers together
        for var, expr in zip(variables, initializers):
            # if the variable is not modifiable
            if not modifiable(var):
                errormodule.throw('semantic_error', 'Unable to modify unmodifiable l-value', assign_expr)
            # if there is a type mismatch
            if not types.coerce(var.data_type, expr.data_type):
                errormodule.throw('semantic_error', 'Variable type and reassignment type do not match', assign_expr)
            # if there is a compound operator
            if op.type != '=' and not types.numeric(var.data_type):
                # all compound operators only work on numeric types
                errormodule.throw('semantic_error', 'Compound assignment operator invalid for non-numeric type', op)

        # return generate statement
        return StatementNode('Assign', op.type, dict(zip(variables, initializers)))
    # else assume increment and decrement
    else:
        # holds whether or not it is increment of decrement
        increment = assign_expr.content[0].type == '+'
        # check if the root is modifiable
        if not modifiable(root):
            errormodule.throw('semantic_error', 'Unable to modify unmodifiable l-value', assign_expr)
        # check if the root is numeric (as only numeric types accept these operators)
        if not types.numeric(root.data_type):
            errormodule.throw('semantic_error', 'Unable to %s non numeric value' % 'increment' if increment else 'decrement', assign_expr)
        # generate statement
        return StatementNode('Increment' if increment else 'Decrement', root)


# check if a root is modifiable via assignment
def modifiable(root):
    # if it is an identifier check for constant
    if isinstance(root, Identifier):
        return not root.constant
    # if it is being dereferenced check if root is non-constant
    if root.name == 'Dereference':
        return modifiable(root.arguments[1])
    # if the '.' operator is being used check if both root and property are non constant
    elif root.name == 'GetMember':
        return not (modifiable(root.arguments[0]) or root.arguments[1].constant)
    # if subscript is being used check if the root is non-constant
    elif root.name == 'Subscript':
        return not modifiable(root.arguments[1])
    # no other actions are valid, so assume not modifiable
    return False
