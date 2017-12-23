import src.semantics.semantics as semantics
import src.semantics.infer as infer
from src.parser.ASTtools import Token
from src.errormodule import throw


# main variable parsing method
def var_parse(variable):
    # a list of modifiers (ie. private, final)
    properties = []
    # creates a temporary holder
    var = semantics.TypedVariable()
    for item in variable.content:
        # gets the modifiers as list
        if item.name == "modifiers":
            properties += infer.unparse(item)
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
                iden = infer.compile_identifier(item)
                var.name = iden[0]
                var.group = iden[1]
                var.is_instance = iden[2]
            # gets data type from extension
            elif item.name == "extension":
                var.data_type = infer.from_type(item.content[1])
                has_extension = True
            # infers data type from the initializer/checks extension v initializer
            elif item.name == "initializer":
                has_init = True
                # if there is no extension, infer
                if not has_extension:
                    var.data_type = infer.from_assignment(item)
                else:
                    # if there is an extension, check it v the item it is being assigned too
                    dt = infer.from_assignment(item)
                    # catches initialization type mismatch
                    # if dt == var.data_type:
                    #    throw("semantic_error", "Declared type and assigned type are not equal", item)
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
            continue
        # generate modifiers
        if item.name == "modifiers":
            func_var.modifiers = infer.unparse(item)
        # generate identifier
        elif item.name == "id":
            identifier = infer.compile_identifier(item)
            func_var.name = identifier[0]
            func_var.group = identifier[1]
            if identifier[2]:
                throw("semantic_error", "Invalid Identifier", item.content[0])
        # generate return type
        elif item.name == "rt_type":
            if isinstance(item.content[0], Token):
                func_var.return_type = None
            elif item.content[0].name == "id":
                # TODO check identifier
                func_var.return_type = infer.compile_identifier(item.content[0])
            else:
                func_var.return_type = infer.from_type(item.content[0].content)
        # parse the function params
        # TODO add param function
        elif item.name == "func_params_decl":
            pass


# parses macros
def macro_parse(macro):
    # holder
    macro_var = semantics.Function()
    # set the data structure
    macro_var.data_structure = semantics.DataStructure.MACRO
    # set the *pseudo* return type
    macro_var.return_type = None
    # parsing loop
    for item in macro.content[1:]:
        # avoid tokens
        if isinstance(item, Token):
            continue
        # generate modifiers
        if item.name == "modifiers":
            macro_var.modifiers = infer.unparse(item)
        # generate identifier
        elif item.name == "id":
            identifier = infer.compile_identifier(item)
            macro_var.name = identifier[0]
            macro_var.group = identifier[1]
            if identifier[2]:
                throw("semantic_error", "Invalid Identifier", item.content[0])
        # parse the parameters
        # TODO parse the parameters
        elif item.name == "macro_params_decl":
            pass
    return macro_var


# parsed structs, interfaces, and types
def struct_parse(struct):
    # holder
    struct_var = semantics.Variable()
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
        struct_var.modifiers = infer.unparse(struct.content[1])
        id_pos = 2
    identifier = infer.compile_identifier(struct.content[id_pos])
    struct_var.name = identifier[0]
    struct_var.group = identifier[1]
    struct_var.is_instance = identifier[2]
    return struct_var


def constructor_parse(constructor):
    pass


# module parser
def module_parse(mod):
    # holder
    mod_var = semantics.Module()
    # set data structure
    mod_var.data_structure = semantics.DataStructure.MODULE
    # slice so that the module keyword is not included
    for item in mod.content[1:]:
        # get modifiers
        if item.name == "modifiers":
            mod_var.modifiers = infer.unparse(item)
        # set the type
        elif item.name == "module_type":
            mod_types = {
                "ACTIVE": semantics.ModuleTypes.ACTIVE,
                "AWAIT": semantics.ModuleTypes.AWAIT,
                "PASSIVE": semantics.ModuleTypes.PASSIVE
            }
            mod_var.mod_type = mod_types[item.content[0].name]
        # compile the identifier
        elif item.name == "id":
            identifier = infer.compile_identifier(item)
            mod_var.name = identifier[0]
            mod_var.group = identifier[1]
            mod_var.is_instance = identifier[2]
        # handle inherits
        elif item.name == "inherit":
            inherits = infer.unparse(item)
            for token in inherits:
                if token.type == ":":
                    inherits.remove(token)
            mod_var.inherit = inherits
    return mod_var



