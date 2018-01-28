import src.semantics.symbols.variables as variables
from src.parser.ASTtools import ASTNode
from src.semantics.semantics import SemanticConstruct
import src.errormodule as er
# package management
from lib.spm import load_package
import pickle
import os

declarations = {
    "variable_declaration": variables.var_parse,
    "struct_block": variables.struct_parse,
    "interface_block": variables.struct_parse,
    "type_block": variables.struct_parse,
    "func_block": variables.func_parse,
    "async_block": variables.func_parse,
    "constructor_block": variables.func_parse
}


class Package:
    def __init__(self):
        self.alias = ""
        self.dep_dir = ""
        self.source_dir = ""
        self.used = False
        self.is_global = False


def import_package(name, is_global, used):
    er_code, er_file = er.file, er.code
    ast = load_package(name)
    os.chdir(os.path.dirname(os.path.abspath(er_file)))
    construct = SemanticConstruct(construct_symbol_table(ast), ast)
    pkg_dir = er.file
    er.code = er_code
    er.file = er_file
    if "/" in name:
        alias = name.split(".")[0].split("/")[-1]
    else:
        alias = name
    os.chdir(os.path.dirname(er.main_file))
    with open("_build/%s_ssc.pickle" % alias, "bw+") as file:
        pickle.dump(construct, file)
        file.close()
    os.chdir(os.path.dirname(os.path.abspath(er.file)))
    pkg = Package()
    pkg.alias = alias
    pkg.dep_dir = "_build/%s_scc.pickle" % alias
    pkg.is_global = is_global
    pkg.source_dir = pkg_dir
    pkg.used = used
    return pkg


# builds the symbol table
def construct_symbol_table(ast):
    symbol_table = []
    for item in ast.content:
        if isinstance(item, ASTNode):
            if item.name == "block":
                symbol_table.append(construct_symbol_table(item))
            elif item.name in declarations:
                if item.name in ["func_block", "async_block", "constructor_block"]:
                    func = variables.func_parse(item)
                    for sub_tree in item.content:
                        if isinstance(sub_tree, ASTNode):
                            if sub_tree.name == "functional_block":
                                if sub_tree.content[0].type != ";":
                                    func.code = SemanticConstruct(construct_symbol_table(sub_tree.content[1]), sub_tree.content[1])
                    symbol_table.append(func)
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
            elif item.name == "include_stmt":
                used = False
                is_global = False
                for elem in item.content:
                    if isinstance(elem, ASTNode):
                        if elem.name == "include_ext":
                            name = elem.content[0]
                            if name.type == "IDENTIFIER":
                                symbol_table.append(import_package(name.value, is_global, used))
                            else:
                                name_str = name.value
                                symbol_table.append(import_package(name_str[1:len(name_str) - 1] + ".sy", is_global, used))
                        else:
                            if elem.content[0].type == "USE":
                                used = True
                            else:
                                is_global = True
            else:
                construct_symbol_table(item)
    return symbol_table
