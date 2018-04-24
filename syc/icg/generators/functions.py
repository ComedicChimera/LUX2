from syc.parser.ASTtools import ASTNode
from syc.icg.types import generate_type, coerce
import errormodule


# generates the declared list of params for any function (an array of symbols)
def generate_parameter_list(decl_params):
    # holds all known parameters
    params = [generate_parameter(decl_params)]  # generate first parameter
    ending = decl_params.content[-1]
    # check for trailing parameters
    if isinstance(ending, ASTNode):
        while ending.name == 'n_func_params':
            # func_params_decl -> n_func_params -> n_func_param
            params.append(generate_parameter(ending.content[1]))
            # update while loop
            ending = ending.content[-1]
    # iterate through params to ensure that they are valid
    # has encountered "optional" parameter
    optional = False
    # has encountered "indefinite" parameter
    indefinite = False
    for param in params:
        # only one indefinite parameter per function and must be the final parameter
        if indefinite:
            errormodule.throw('semantic_error', 'A function\'s indefinite parameter must be the last parameter', decl_params)
        # if it has the property indefinite, it is indefinite
        elif hasattr(param, 'indefinite'):
            indefinite = True
        # if it has a default_value, it is optional
        elif hasattr(param, 'default_value'):
            optional = True
        # if there has been an optional param, and this param is not optional, throw param order exception
        elif optional:
            errormodule.throw('semantic_error', 'Normal parameter preceded by optional parameter', decl_params)


def generate_parameter(decl_params):
    # holds working parameters
    param = {}
    for item in decl_params.content:
        if isinstance(item, ASTNode):
            # handle parameter prefix
            if item.name == 'func_param_prefix':
                # add passing by reference
                if item.content[0].type == 'AMP':
                    param['reference'] = True
                # add constant parameters
                elif item.content[0].type == '@':
                    param['const'] = True
            # specify type
            elif item.name == 'extension':
                param['data_type'] = generate_type(item.content[-1])
            # handle initializer
            elif item.name == 'initializer':
                param['default_value'] = generate_expr(item.content[-1])
        else:
            # handle indefinite params
            if item.type == '~':
                param['indefinite'] = True
            # add name
            elif item.type == 'IDENTIFIER':
                param['name'] = item.value
    # generate parameter object
    return type('Object', (), param)


# get the return type from a function body
# TODO merge with general block parser (to allow id checking and such)
def get_return_type(function_body):
    # return type holder
    rt_type = None
    # if it has encountered a return value
    is_rt_type = False
    # if it is a generator
    generator = False
    for item in function_body.content:
        if isinstance(item, ASTNode):
            if item.name == 'return_stmt':
                if len(item.content) > 1:
                    # generate new type from return expr
                    n_type = generate_expr(item.content[1].content[0]).data_type
                    # if they are not equal and there is a return type
                    if n_type != rt_type and is_rt_type and not coerce(rt_type, n_type):
                        errormodule.throw('semantic_error', 'Inconsistent return type', item)
                    else:
                        rt_type = n_type
                else:
                    # if the there is an rt type and it is not null
                    if is_rt_type and rt_type:
                        errormodule.throw('semantic_error', 'Inconsistent return type', item)
                        # no need to update as it is already null
                is_rt_type = True
            elif item.name == 'yield_stmt':
                if len(item.content) > 1:
                    # generate new type from return expr
                    n_type = generate_expr(item.content[1].content[0]).data_type
                    # if they are not equal and there is a return type
                    if n_type != rt_type and is_rt_type and not coerce(rt_type, n_type):
                        errormodule.throw('semantic_error', 'Inconsistent return type', item)
                    else:
                        rt_type = n_type
                else:
                    # if the there is an rt type and it is not null
                    if is_rt_type and rt_type:
                        errormodule.throw('semantic_error', 'Inconsistent return type', item)
                        # no need to update as it is already null
                is_rt_type = True
                generator = True
            else:
                # get type from rest of function
                temp_type = get_return_type(item)
                # if the types are inconsistent
                if is_rt_type and temp_type != rt_type:
                    errormodule.throw('semantic_error', 'Inconsistent return type', item)
                # otherwise update return type
                else:
                    rt_type = temp_type
    # since rt_type will be evaluated on the basis of not being a direct data type
    # return None is ok
    return rt_type, generator


def check_parameters(func, params):
    pass


def get_return_from_type(rt_type):
    return rt_type


from syc.icg.generators.expr import generate_expr