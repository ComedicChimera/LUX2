import src.semantics.semantics as semantics
import src.semantics.symbols.types as types
from src.errormodule import throw
from src.parser.ASTtools import Token
from src.semantics.symbols.parameters import parse_parameters


# main variable parsing method
def var_parse(variable):
    # a list of modifiers (ie. private, final)
    properties = []
    # creates a temporary holder
    var = semantics.TypedVariable()
    for item in variable.content:
        # gets the modifiers as list
        if item.name == "modifiers":
            properties += types.unparse(item)
        # runs the parse on the declaration itself (sans modifiers)
        elif item.name == "variable_decl_stmt":
            var = variable_declaration_parse(item)
            var.modifiers = properties
    return var


# main declaration parsing function
def variable_declaration_parse(var_decl):
    # another temporary holder
    var = semantics.TypedVariable()
    # will be used to decide whether or not type needs to be inferred, checked or none
    has_extension = False
    # if variable has been initialized
    has_init = False
    for item in var_decl.content:
        # checks for constants
        if isinstance(item, Token):
            if item.type == "AMP":
                var.data_structure = semantics.DataStructure.CONSTANT
        else:
            # generates the identifier properties
            if item.name == "id":
                iden = types.compile_identifier(item)
                var.name = iden[0]
                var.group = iden[1]
                var.is_instance = iden[2]
            # gets data type from extension
            elif item.name == "extension":
                var.data_type = types.from_type(item.content[1])
                has_extension = True
            # infers data type from the initializer
            elif item.name == "initializer":
                var.initializer = item.content[1]
                has_init = True
                if has_extension:
                    var.data_type = "INFER"
    # catches invalid null declarations
    if not has_init and not has_extension:
        throw("semantic_error", "Unable to discern type from declaration", var_decl)
    return var


# parses functions
def func_parse(func):
    # holder
    func_var = semantics.Function()
    # parsing loop
    for item in func.content[1:]:
        # avoid tokens
        if isinstance(item, Token):
            if item.type == "ASYNC":
                func_var.is_async = True
            elif item.type == "CONSTRUCTOR":
                func_var.is_constructor = True
            continue
        # generate modifiers
        if item.name == "modifiers":
            func_var.modifiers = types.unparse(item)
        # generate identifier
        elif item.name == "id":
            identifier = types.compile_identifier(item)
            func_var.name = identifier[0]
            func_var.group = identifier[1]
            if identifier[2]:
                throw("semantic_error", "Invalid Identifier", item.content[0])
        # generate return type
        elif item.name == "rt_type":
            types.from_type(item.content[1])
            # parse the function params
            if item.name == "func_params_decl":
                func_var.parameters = parse_parameters(item)
    return func_var


# parsed structs, interfaces, and types
def struct_parse(struct):
    # holder
    struct_var = semantics.Structure()
    # decides what type it is
    if struct.content[0].type == "STRUCT":
        struct_var.data_structure = semantics.DataStructure.STRUCT
    elif struct.content[0].type == "TYPE":
        struct_var.data_structure = semantics.DataStructure.TYPE
    else:
        struct_var.data_structure = semantics.DataStructure.INTERFACE
    # gets its identifiers and modifiers
    id_pos = 1
    if struct.content[1].name == "modifiers":
        struct_var.modifiers = types.unparse(struct.content[1])
        id_pos = 2
    identifier = types.compile_identifier(struct.content[id_pos])
    struct_var.name = identifier[0]
    struct_var.group = identifier[1]
    struct_var.is_instance = identifier[2]
    struct_var.members = parse_members(struct.content[-2], struct.content[0].type)
    return struct_var


def parse_members(s_members, s_type):
    if s_type == "STRUCT":
        return parse_struct_members(s_members)
    elif s_type == "INTERFACE":
        return parse_interface_members(s_members)
    else:
        return types.remove_periods(s_members)


def parse_struct_members(m):
    var = semantics.TypedVariable()
    members = []
    for item in m.content:
        if not isinstance(item, Token):
            if item.name == "extension":
                var.data_type = types.from_type(item.content[1])
            elif item.name == "n_var":
                members.append(var)
                members += parse_struct_members(item)
                return members
        else:
            if item.type == "IDENTIFIER":
                var.name = item.value
    members.append(var)
    return members


def parse_interface_members(m):
    func = semantics.Function()
    members = []
    for item in m.content:
        if not isinstance(item, Token):
            if item.name == "modifiers":
                func.modifiers = types.unparse(item)
            elif item.name == "rt_type":
                if isinstance(item.content[0], Token):
                    func.return_type = None
                elif item.content[0].name == "id":
                    func.return_type = types.compile_identifier(item.content[0])
                else:
                    func.return_type = types.from_type(item.content[0].content)
            elif item.name == "id":
                identifier = types.compile_identifier(item)
                func.name = identifier[0]
                func.group = identifier[1]
                if identifier[2]:
                    throw("semantic_error", "Invalid Identifier", item.content[0])
            elif item.name == "func_params_decl":
                func = parse_parameters(item)
            elif item.name == "interface_main":
                members.append(func)
                members += parse_interface_members(item)
                return members
    members.append(func)
    return members


# module parser
def module_parse(mod):
    # holder
    mod_var = semantics.Module()
    # set data structure
    mod_var.data_structure = semantics.DataStructure.MODULE
    # slice so that the module keyword is not included
    for item in mod.content[1:]:
        # check for tokens
        if isinstance(item, Token):
            continue
        # get modifiers
        elif item.name == "modifiers":
            mod_var.modifiers = types.unparse(item)
        # set the type
        elif item.name == "module_type":
            mod_types = {
                "ACTIVE": semantics.ModuleTypes.ACTIVE,
                "AWAIT": semantics.ModuleTypes.AWAIT,
                "PASSIVE": semantics.ModuleTypes.PASSIVE
            }
            mod_var.mod_type = mod_types[item.content[0].type]
        # compile the identifier
        elif item.name == "id":
            identifier = types.compile_identifier(item)
            mod_var.name = identifier[0]
            mod_var.group = identifier[1]
            mod_var.is_instance = identifier[2]
        # handle inherits
        elif item.name == "inherit":
            inherits = types.unparse(item)
            for token in inherits:
                if token.type == ":":
                    inherits.remove(token)
            mod_var.inherit = inherits
    return mod_var


# parses module constructors
def module_constructor_parse(constructor):
    c_var = semantics.Function()
    c_var.is_constructor = True
    for item in constructor.content:
        if not isinstance(item, Token):
            if item.name == "func_params_decl":
                c_var.parameters = parse_parameters(item)
    return c_var
