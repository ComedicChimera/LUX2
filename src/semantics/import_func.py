from lib.spm import load_package
from src.parser.lexer import Lexer
import src.errormodule as er
from src.parser.syc_parser import Parser
from src.semantics.symbol_management.symbols import construct_symbol_table
from src.semantics.semantics import SemanticConstruct
import pickle


class Package:
    def __init__(self):
        self.alias = ""
        self.dir = ""
        self.is_global = False


def import_package(name, is_global, alias):
    code = load_package(name)
    er_file = er.file
    er_code = er.code
    lx = Lexer()
    tokens = lx.lex(code)
    p = Parser(tokens)
    ast = p.parse()
    s_table = construct_symbol_table(ast)
    construct = SemanticConstruct(s_table, ast)
    er.code = er_code
    er.file = er_file
    pickle.dump(construct, "_build/bin/%s_scc.pickle" % alias)
    pkg = Package()
    pkg.alias = alias
    pkg.dir = "_build/bin/%s_scc.pickle" % alias
    pkg.is_global = is_global
    return pkg


