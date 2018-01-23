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
    "macro_block": variables.macro_parse,
    "async_block": variables.func_parse,
    "constructor_block": variables.func_parse
}


class Package:
    def __init__(self):
        self.alias = ""
        self.dir = ""


def import_package(name, is_global):
    """er_code = er.code
    er_file = er.file
    ast = load_package(name)
    s_table = construct_symbol_table(ast)
    construct = SemanticConstruct(s_table, ast)
    er.code = er_code
    er.file = er_file
    if "/" in name:
        alias = name.split(".")[0].split("/")[-1]
    else:
        alias = name
    os.chdir(os.path.dirname(er.main_file))
    with open("_build/bin/%s_ssc.pickle" % alias, "bw+") as file:
        pickle.dump(construct, file)
        file.close()
    if os.getcwd() != os.path.dirname(er.file):
        os.chdir(os.path.dirname(er.file))
    pkg = Package()
    pkg.alias = alias
    pkg.dir = "_build/bin/%s_scc.pickle" % alias
    pkg.is_global = is_global
    return pkg"""
    return name


# builds the symbol table
def construct_symbol_table(ast, scope=0):
    symbol_table = []
    for item in ast.content:
        if isinstance(item, ASTNode):
            if item.name == "block":
                symbol_table.append(construct_symbol_table(item, scope + 1))
            elif item.name in declarations:
                variables.s_table = symbol_table
                if item.name in ["func_block", "variable_declaration", "async_block", "constructor_block", "interface_block"]:
                    if item.name in ["func_block", "async_block", "constructor_block"]:
                        func = variables.func_parse(item, scope)
                        for sub_tree in item.content:
                            if isinstance(sub_tree, ASTNode):
                                if sub_tree.name == "functional_block":
                                    func.code = SemanticConstruct(construct_symbol_table(sub_tree.content[1]), sub_tree.content[1])
                        symbol_table.append(func)
                    elif item.name == "interface_block":
                        symbol_table.append(variables.struct_parse(item, scope))
                    else:
                        var = declarations[item.name](item, scope)
                        symbol_table.append(var)
                else:
                    if item.name == "macro_block":
                        macro = variables.macro_parse(item)
                        for sub_tree in item.content:
                            if isinstance(sub_tree, ASTNode):
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
            elif item.name == "include_stmt":
                if item.content[1].content[0].type == "IDENTIFIER":
                    name = item.content[1].content[0].value
                else:
                    name = item.content[1].content[0].value
                    name = name[1:len(name) - 1] + ".sy"
                # try:
                    symbol_table.append(import_package(name, True))
                # except Exception as e:
                    # er.throw("package_error", e, item)
            else:
                construct_symbol_table(item, scope)
    return symbol_table
