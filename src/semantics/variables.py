import src.semantics.semantics as semantics
import src.semantics.infer as infer
from src.parser.ASTtools import Token


def compile_identifier(id):
    if len(id.content) < 2:
        return [id.content[0].value, []]
    else:
        return [id.content[-1].value, infer.unparse(id.content[1:])]


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
            properties += infer.unparse(item)
        elif item.name == "variable_decl_stmt":
            var = variable_declaration_parse(item)
            var.modifiers = properties
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
                properties["data_type"] = infer.from_type(item.content[1])
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
