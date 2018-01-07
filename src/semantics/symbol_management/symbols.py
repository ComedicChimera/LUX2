import src.semantics.symbol_management.variables as variables
from src.parser.ASTtools import ASTNode
from src.semantics.semantics import SemanticConstruct
import src.errormodule as er
# package management
from lib.spm import load_package
import pickle
from src.parser.syc_parser import Parser
from src.parser.lexer import Lexer
import src.semantics.semantics as semantics

declarations = {
    "variable_declaration": variables.var_parse,
    "struct_block": variables.struct_parse,
    "interface_block": variables.struct_parse,
    "type_block": variables.struct_parse,
    "func_block": variables.func_parse,
    "macro_block": variables.macro_parse,
    "async_block": variables.func_parse,
    "constructor_block": variables.func_parse
}


class Package:
    def __init__(self):
        self.alias = ""
        self.dir = ""
        self.is_global = False


def import_package(name, is_global):
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
    if "/" in name:
        alias = name.split(".")[0].split("/")[-1]
    else:
        alias = name
    with open("_build/bin/%s_ssc.pickle" % alias, "bw+") as file:
        pickle.dump(construct, file)
        file.close()
    pkg = Package()
    pkg.alias = alias
    pkg.dir = "_build/bin/%s_scc.pickle" % alias
    pkg.is_global = is_global
    return pkg


# builds the symbol table
def construct_symbol_table(ast, scope=0):
    symbol_table = []
    for item in ast.content:
        if isinstance(item, ASTNode):
            if item.name == "block":
                symbol_table.append(construct_symbol_table(item, scope + 1))
            elif item.name in declarations:
                variables.s_table = symbol_table
                if item.name in ["func_block", "variable_declaration", "async_block", "constructor_block"]:
                    if item.name in ["func_block", "async_block", "constructor_block"]:
                        func = variables.func_parse(item, scope)

                        for sub_tree in item.content:
                            if isinstance(sub_tree, ASTNode):
                                if sub_tree.name == "functional_block":
                                    func.code = SemanticConstruct(construct_symbol_table(sub_tree.content[1]), sub_tree.content[1])
                        symbol_table.append(func)
                    else:
                        var = declarations[item.name](item, scope)
                        if var.data_type == semantics.DataTypes.PACKAGE:
                            current = ""
                            for elem in item.content:
                                if isinstance(elem, ASTNode):
                                    if elem.name == 'initializer':
                                        current = elem.content[1]
                            while current.name != "import_call":
                                current = current.content[0]
                            name = current.content[2].value
                            var.data_type = import_package(name, False)
                        symbol_table.append(var)
                else:
                    if item.name == "macro_block":
                        macro = variables.macro_parse(item)
                        for sub_tree in item.content:
                            if sub_tree.name == "functional_block":
                                macro.code = SemanticConstruct(construct_symbol_table(sub_tree.content[1]), sub_tree.content[1])
                        symbol_table.append(macro)
                    else:
                        symbol_table.append(declarations[item.name](item))
            elif item.name == "module_block":
                mod = variables.module_parse(item)
                for sub_tree in item.content:
                    if isinstance(sub_tree, ASTNode):
                        if sub_tree.name == "module_main":
                            mod.constructor = variables.module_constructor_parse(sub_tree.content[0])
                            for component in sub_tree.content[0].content:
                                if isinstance(component, ASTNode):
                                    if component.name == "constructional_block":
                                        if isinstance(component.content[0], ASTNode):
                                            mod.constructor.code = SemanticConstruct(construct_symbol_table(component.content[0]), component.content[0])
                            if len(sub_tree.content) > 1:
                                mod.members = sub_tree.content[1]
                symbol_table.append(mod)
            elif item.name == "import_stmt":
                name = item.content[3].value
                symbol_table.append(import_package(name[1:len(name) - 1], True))
            else:
                construct_symbol_table(item, scope)
    return symbol_table
