# import errormodule as er


# a class to hold identifiers for the symbol table
class Identifier:
    def __init__(self, name, data_type, modifiers):
        self.name = name
        self.data_type = data_type
        self.modifiers = modifiers


# a holder for all components of the sem ast necessary for intermediate code generation
class SemanticAST:
    def __init__(self, symbol_table, modified_ast, activation_tree):
        self.activation_tree = activation_tree
        self.symbol_table = symbol_table
        self.modified_ast = modified_ast


# runs the semantic analyzer
def sem_analyze(ast):
    symbol_table = get_s_table(ast)
    activation_tree = generate_activation_tree(ast)
    sem_ast = proof(ast, symbol_table, activation_tree)
    sem_obj = SemanticAST(symbol_table, sem_ast, activation_tree)
    return sem_obj


# gets the semantically valid modified ast and checks current ast
def proof(ast, symbol_table, activation_tree):
    return ast


# generates the activation tree
def generate_activation_tree(ast):
    return ast


# generates the symbol table
def get_s_table(ast):
    return ast
