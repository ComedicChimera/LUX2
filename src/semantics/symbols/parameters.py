from src.errormodule import throw
from src.parser.ASTtools import ASTNode
from src.semantics.symbols.types import from_type


# main parameter class
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


# checks if optional param is valid
# no check for indefinite as it is handled by grammar
def check_optional(p):
    # stores whether an optional parameter has occurred
    is_opt = False
    # iterate through generated parameters
    for item in p:
        # if previous item was optional and current is not, throw error (optional parameters declared before reg params
        if is_opt and not item.optional:
            # TODO get erroneous element
            throw("semantic_error", "Optional parameters declared before regular parameters", "")
        is_opt = item.optional


# main parameter parse function
def parse_parameters(params):
    # final params
    n_params = []
    # working param
    param = []
    # iterate through parameters
    for item in params.content:
        if isinstance(item, ASTNode):
            # generate next two parameters
            n_params.append(generate_func_parameter(param))
            n_params.append(generate_func_parameter(item.content[1].content))
            # continue recursively
            n_params += parse_parameters(item.content[2])
            break
        param.append(item)
    else:
        # catch single parameter function
        n_params.append(generate_func_parameter(param))
    # check optional parameters
    check_optional(n_params)
    return n_params


# generates a functional parameters based on list
def generate_func_parameter(p):
    parameter = Parameter()
    for item in p:
        if isinstance(item, ASTNode):
            if item.name == "func_param_prefix":
                if item.content[0].type == "AMP":
                    parameter.reference = True
                elif item.content[0].type == "@":
                    parameter.const = True
            elif item.name == "extension":
                parameter.data_type = from_type(item.content[1])
            elif item.name == "params_extension":
                parameter.default = item
        else:
            if item.type == "*":
                parameter.indefinite = True
            elif item.type == "THIS":
                parameter.instance_marker = True
            elif item.type == "IDENTIFIER":
                parameter.name = item.value
    return parameter

