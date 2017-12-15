import src.semantics as semantics
from src.ASTtools import Token
import src.infer as infer


def compile_identifier(id):
    return id.content


def create_variable(properties):
    var = semantics.TypedVariable()
    var.name = properties["name"]
    var.data_type = properties["data_type"]
    if "group" in properties.keys():
        var.group = properties["group"]
    if properties["var_type"] == "CONST":
        var.is_const = True
    return var


def var_parse(variable):
    properties = []
    var = semantics.TypedVariable()
    for item in variable.content:
        if item.name == "modifiers":
            properties += item.content
        elif item.name == "var_decl_stmt":
            var = variable_declaration_parse(item)
            var.properties = properties
    return var


def variable_declaration_parse(var_decl):
    properties = {}
    for item in var_decl.content:
        if isinstance(item, Token):
            if item.type == "DOLLAR":
                properties["var_type"] = "VAR"
            elif item.type == "AMP":
                properties["var_type"] = "CONST"
        else:
            if item.name == "id":
                iden = compile_identifier(item)
                properties["name"] = iden[0]
                properties["group"] = iden[1]
            elif item.name == "extension":
                properties["data_type"] = infer.from_extension(item)
                return create_variable(properties)
            elif item.name == "initializer":
                properties["data_type"] = infer.from_assignment(item)
                return create_variable(properties)


def func_parse(func):
    pass


def macro_parse(macro):
    pass


def struct_parse(struct):
    pass


def module_parse(mod):
    pass
