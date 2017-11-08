# import errormodule as er
import src.ASTtools as AST
# from util import *
symbol_table = {}


# parses the various declarations
class DeclarationParser:
    def __init__(self):
        pass

    @staticmethod
    def parse_func(node):
        pass

    @staticmethod
    def parse_var(node):
        pass

    @staticmethod
    def parse_ptr(node):
        pass

    @staticmethod
    def parse_macro(node):
        pass

    @staticmethod
    def parse_constructor(node):
        pass


decl_stmts = {
                 "func_block": DeclarationParser.parse_func,
                 "var_decl": DeclarationParser.parse_var,
                 "macro_block": DeclarationParser.parse_macro,
                 "pointer_decl": DeclarationParser.parse_ptr,
                 "constructor_block": DeclarationParser.parse_constructor,
                 "constructor_stmt": DeclarationParser.parse_constructor,
                 "fwd_decl": None
}


# a class to hold identifiers for the symbol table
class Identifier:
    def __init__(self, name, data_type, modifiers, is_grouped, id_type):
        self.name = name
        self.data_type = data_type
        self.modifiers = modifiers
        self.is_grouped = is_grouped
        self.id_type = id_type
        self.params = []


# a holder for all components of the sem ast necessary for intermediate code generation
class SemanticAST:
    def __init__(self, symbol_table, modified_ast, activation_tree):
        self.activation_tree = activation_tree
        self.symbol_table = symbol_table
        self.modified_ast = modified_ast


# runs the semantic analyzer
def sem_analyze(ast):
    global symbol_table
    activation_tree = generate_activation_tree(ast)
    symbol_table += get_s_table(ast, activation_tree)
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
    for item in activation_tree:
        if item in decl_stmts.keys():
            scope_id = str(pos) + " " + str(scope)
            s_table[scope_id] = get_symbol_data(ast, pos)
        pos += 1
    return ast


# finds the actual tree given based on the activation tree
def get_symbol_data(ast, pos):
    count = 0
    for item in ast:
        if count == pos:
            return interpret_content(item)
        elif isinstance(item, AST.ASTNode):
            return get_symbol_data(ast, pos - count)
        count += 1


# decides which parser to use to parser the node and how to feed the node into it
def interpret_content(node):
    if node.name == "fwd_decl":
        return interpret_content(node.content[0])
    elif node.name == "func_block" or "macro_block":
        return decl_stmts[node.name](node.content[0])
    elif node.name == "func_decl" or "macro_decl":
        return decl_stmts[node.name.split("_")[0] + "_block"](node)
    else:
        return decl_stmts[node.name](node)

