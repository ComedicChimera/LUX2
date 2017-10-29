# import errormodule as er
import ASTtools as AST


# a class to hold identifiers for the symbol table
class Identifier:
    def __init__(self, name, data_type, modifiers, is_grouped):
        self.name = name
        self.data_type = data_type
        self.modifiers = modifiers
        self.is_grouped = is_grouped


class MacroIdentifier:
    def __init__(self, name, params, modifiers, is_forward, is_grouped):
        self.name = name
        self.params = params
        self.modifiers = modifiers
        self.is_forward = is_forward
        self.is_grouped = is_grouped


class FuncIdentifier:
    def __init__(self, name, params, return_type, modifiers, is_forward, is_grouped):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.modifiers = modifiers
        self.is_forward = is_forward
        self.is_grouped = is_grouped


# a holder for all components of the sem ast necessary for intermediate code generation
class SemanticAST:
    def __init__(self, symbol_table, modified_ast, activation_tree):
        self.activation_tree = activation_tree
        self.symbol_table = symbol_table
        self.modified_ast = modified_ast


# runs the semantic analyzer
def sem_analyze(ast):
    activation_tree = generate_activation_tree(ast)
    symbol_table = get_s_table(ast, activation_tree)
    sem_ast = proof(ast, symbol_table, activation_tree)
    sem_obj = SemanticAST(symbol_table, sem_ast, activation_tree)
    return sem_obj


# gets the semantically valid modified ast and checks current ast
def proof(ast, symbol_table, activation_tree):
    return ast


# generates the activation tree
def generate_activation_tree(ast):
    # primes activation list
    activation_tree = []
    # iterates through the current AST content
    for item in ast.content:
        # if the item is an AST Node, recurs and adds the data to the list
        if isinstance(item, AST.ASTNode):
            activation_tree += generate_activation_tree(item)
            # adds the name of the AST to the list
            activation_tree.append(item.name)
    return activation_tree


# generates the symbol table
def get_s_table(ast, activation_tree):
    s_table = {}
    pos = 0
    scope = 0
    decl_stmts = []
    for item in activation_tree:
        if item in decl_stmts:
            scope_id = str(pos) + " " + str(scope)
            s_table[scope_id] = get_symbol_data(ast, item, pos)
    return ast


def get_symbol_data(ast, name, pos):
    count = 0
    for item in ast:
        if count == pos:
            return interpret_content(item)
        elif isinstance(item, AST.ASTNode):
            count += 1


def interpret_content(node):
    info = []
    stmt = node.content[0].content
    has_access_modifiers = False
    if node.name == "macro_block":
        info.append(["symbol_type", "macro"])
        if stmt[1].name == "var_modifiers":
            mod_data = get_modifiers(stmt[1])
            info += mod_data[0]
            has_access_modifiers = mod_data[1]
            if len(stmt[2].content) == 1 and has_access_modifiers:
                raise CustomException("Un-grouped macro cannot have access modifiers.")
            elif len(stmt[2].content) == 1:
                info.append(["NAME", stmt[2].content[0]])
            else:
                info.append(["NAME", stmt[2].content.join()])
                info.append("IS_GROUPED")
        else:
            if len(stmt[1].content) == 1 and has_access_modifiers:
                raise CustomException("Un-grouped macro cannot have access modifiers.")
            elif len(stmt[1].content) == 1:
                info.append(["NAME", stmt[1].content[0]])
            else:
                info.append(["NAME", stmt[1].content.join()])
                info.append("IS_GROUPED")
        # get params
    elif node.name == "func_block":
        pass
    else:
        pass


def get_modifiers(node):
    modifiers = []
    ham = False
    for item in node.content:
        if item.name == "access_modifiers":
            modifiers.append(["ACCESS_MODIFIERS", item.content[0]])
            ham = True
        else:
            modifiers.append(["MODIFIER", item.content[0]])
    return [modifiers, ham]


class CustomException(Exception):
    pass
