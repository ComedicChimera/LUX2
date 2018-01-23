from src.errormodule import throw
from src.parser.ASTtools import ASTNode
from src.semantics.symbols.types import from_type


class Parameter:
    def __init__(self):
        self.name = ""
        self.data_type = None
        self.optional = False
        self.indefinite = False
        self.reference = False
        self.instance_marker = False
        self.default = None
        self.const = False


def check_optional(p):
    for item in p:
        is_opt = item.optional
        if is_opt and not item.optional:
            throw("semantic_error", "Optional parameters declared before regular parameters", "")


def parse_parameters(params):
    n_params = []
    param = []
    is_func = False
    for item in params.content:
        if isinstance(item, ASTNode):
            if item.name == "n_var":
                n_params.append(generate_macro_parameter(param))
                n_params += parse_parameters(item)
                break
            elif item.name == "n_func_params":
                is_func = True
                n_params.append(generate_func_parameter(param))
                n_params.append(generate_func_parameter(item.content[1].content))
                n_params += parse_parameters(item.content[2])
                break
        param.append(item)
    else:
        if is_func:
            n_params.append(generate_func_parameter(param))
        else:
            n_params.append(generate_macro_parameter(param))
    check_optional(n_params)
    return n_params


def generate_macro_parameter(p):
    parameter = Parameter()
    for item in p:
        if isinstance(item, ASTNode):
            if item.name == "extension":
                parameter.data_type = from_type(item.content[1])
        elif item.type == "IDENTIFIER":
            parameter.name = item.value
        elif item.type == "THIS":
            parameter.instance_marker = True
    return parameter


def generate_func_parameter(p):
    parameter = Parameter()
    for item in p:
        if isinstance(item, ASTNode):
            if item.name == "func_param_prefix":
                if item.content[0].type == "@":
                    parameter.reference = True
                elif item.content[0].type == "AMP":
                    parameter.const = True
            elif item.name == "extension":
                parameter.data_type = from_type(item.content[1])
            elif item.name == "params_extension":
                parameter.default = item
        else:
            if item.type == "**":
                parameter.indefinite = True
            elif item.type == "THIS":
                parameter.instance_marker = True
            elif item.type == "IDENTIFIER":
                parameter.name = item.value
    return parameter

