import src.semantics.symbols.variables as variables
from src.parser.ASTtools import ASTNode
from src.semantics.semantics import SemanticConstruct
import src.errormodule as er
# package management
import src.semantics.include as pkg
import pickle
from random import randint
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
        # where package was originally located        self.source_dir = ""
        self.used = False
        self.extern = False


def import_package(name, extern, used):
    def get_rand():
        rand = ''
        for _ in range(0, 10):
            rand += str(randint(0, 10))
        return rand

    er_file = er.file
    er_code = er.code
    inclusion = pkg.include(name)
    ast = inclusion[0]
    pkg.load_prefix += inclusion[1]
    sem_obj = SemanticConstruct(construct_symbol_table(ast), ast)
    er.file = er_file
    er.code = er_code
    pkg.load_prefix = pkg.load_prefix[:len(pkg.load_prefix) - len(inclusion[1])]
    num = get_rand()
    if '\\' in name:
        name = name.split('\\')[-1]
    with open(util.output_dir + '_build/%s_scc.pickle' % (name + num), 'bw+') as file:
        pickle.dump(sem_obj, file)
        file.close()
    package = Package()
    package.alias = name
    package.used = used
    package.extern = extern
    package.dep_dir = util.output_dir + '_build/%s_scc.pickle' % (name + num)
    return package


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
                # try:
                    if item.name in ["func_block", "async_block", "constructor_block"]:
                        func = variables.func_parse(item)
                        for sub_tree in item.content:
                            if isinstance(sub_tree, ASTNode):
                                if sub_tree.name == "functional_block":
                                    if sub_tree.content[0].type != ";":
                                        if len(sub_tree.content) > 2:
                                            func.code = SemanticConstruct(construct_symbol_table(sub_tree.content[1]), sub_tree.content[1])
                        symbol_table.append(func)
                    else:
                        symbol_table.append(declarations[item.name](item))
                # except Exception as e:
                # er.throw("semantic_error", e, item)
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
                extern = False
                for elem in item.content:
                    if isinstance(elem, ASTNode):
                        # collect data about package from ast
                        if elem.name == "include_ext":
                            name = elem.content[0]
                            # add import to s-table (id)
                            if name.type == "IDENTIFIER":
                                symbol_table.append(import_package(name.value, extern, used))
                            # import for str
                            else:
                                name_str = name.value
                                symbol_table.append(import_package(name_str[1:len(name_str) - 1] + ".sy", extern, used))
                        elif elem.name == 'extern':
                            extern = True
                        else:
                            if elem.content[0].type == "USE":
                                used = True
            else:
                # add on any new symbols without descending scope
                symbol_table += construct_symbol_table(item)
    return symbol_table
