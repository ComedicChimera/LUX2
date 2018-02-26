import src.semantics.symbols.variables as variables
from src.parser.ASTtools import ASTNode
from src.semantics.semantics import SemanticConstruct
import src.errormodule as er
# package management
from lib.spm import load_package
import pickle
import util

# declaration table for matching
declarations = {
    "variable_declaration": variables.var_parse,
    "struct_block": variables.struct_parse,
    "interface_block": variables.struct_parse,
    "type_block": variables.struct_parse,
    "func_block": variables.func_parse,
    "async_block": variables.func_parse,
    "constructor_block": variables.func_parse
}


# class for holding all packages
class Package:
    def __init__(self):
        self.alias = ""
        # where it is stored during compilation
        self.dep_dir = ""
        # where package was originally located
        self.source_dir = ""
        self.used = False


def import_package(name, is_global, used):
    # create temporary constants for preservation of current working directory
    er_code, er_file = er.file, er.code
    # generate an ast and load a package
    ast = load_package(name)
    # restore previous working dir
    util.chdir(er_file)
    # generate semantic construct
    construct = SemanticConstruct(construct_symbol_table(ast), ast)
    # get original source dir
    pkg_dir = er.file
    # restore working directory for error module
    er.code = er_code
    er.file = er_file
    # generate alias
    if "/" in name:
        alias = name.split(".")[0].split("/")[-1]
    else:
        alias = name
    # return to main file for dependency dumping
    util.chdir(er.main_file)
    with open("_build/%s_ssc.pickle" % alias, "bw+") as file:
        pickle.dump(construct, file)
        file.close()
    # return to current working dir
    util.chdir(er.file)
    # generate package
    pkg = Package()
    pkg.alias = alias
    pkg.dep_dir = "_build/%s_scc.pickle" % alias
    pkg.is_global = is_global
    pkg.source_dir = pkg_dir
    pkg.used = used
    return pkg


# builds the symbol table
def construct_symbol_table(ast):
    # current sub symbol table
    symbol_table = []
    for item in ast.content:
        if isinstance(item, ASTNode):
            # descend scope on blocks
            if item.name in ["block", "sub_scope"]:
                symbol_table.append(construct_symbol_table(item))
            # parse declarations
            elif item.name in declarations:
                try:
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
                except Exception as e:
                    er.throw("semantic_error", e, item)
            # special parsing rules for module blocks
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
                                mod.members = construct_symbol_table(sub_tree.content[1])
                symbol_table.append(mod)
            # power package inclusion
            elif item.name == "include_stmt":
                used = False
                is_global = False
                for elem in item.content:
                    if isinstance(elem, ASTNode):
                        # collect data about package from ast
                        if elem.name == "include_ext":
                            name = elem.content[0]
                            # add import to s-table (id)
                            if name.type == "IDENTIFIER":
                                symbol_table.append(import_package(name.value, is_global, used))
                            # import for str
                            else:
                                name_str = name.value
                                symbol_table.append(import_package(name_str[1:len(name_str) - 1] + ".sy", is_global, used))
                        else:
                            # if elem is prefixed by use
                            if elem.content[0].type == "USE":
                                used = True
            else:
                # add on any new symbols without descending scope
                symbol_table += construct_symbol_table(item)
    return symbol_table
