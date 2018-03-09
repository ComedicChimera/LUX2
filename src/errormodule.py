import re

from src.parser.ASTtools import Token
from util import *

file = "MAIN"

code = ""


# error types
class SycCompileError(Exception):
    pass


def get_position(ndx):
    new_lines = list(re.finditer("\n", code))
    if len(new_lines) == 0:
        return [0, ndx]
    line = 0
    for num in range(len(new_lines)):
        if ndx <= new_lines[num].start():
            if num > 0:
                ndx -= new_lines[num - 1].start() + 1
                break
            else:
                break
        line += 1
    else:
        ndx -= new_lines[-1].start() + 1
    return [line, ndx]


def getln(pos, len_carrots):
    return code.split("\n")[pos[0]] + "\n" + " " * pos[1] + ("^" * len_carrots)


def unparse(ast):
    unwind_list = []
    for item in ast.content:
        if isinstance(item, Token):
            unwind_list.append(item)
        else:
            unwind_list += unparse(item)
    return unwind_list


def throw(type, error, params):
    code_error = Exception()
    error_message = ConsoleColors.RED + "Compile Error occurred in file '%s':\n" % file
    if type == "lex_error":
        pos = get_position(params[1])
        code_error = SycCompileError(error_message + "[Lexical Error] - %s, '%s' (ln:%d, pos:%d)\n" % (error, params[0], pos[0] + 1, pos[1]))
    elif type == "syntax_error":
        if params[0].type == "$":
            token = params[0]
            pos = get_position(token.ndx)
            error_message += "[Syntax Error] - Invalid End of Program, (ln:%d, pos:%d):\n" % (pos[0] + 1, pos[1])
            error_message += getln(pos, len(token.value))
            if not isinstance(params[1], list):
                error_message += "\n\nExpected: '%s'" % params[1]
            code_error = SycCompileError(error_message)
        else:
            token = params[0]
            pos = get_position(token.ndx)
            error_message += "[Syntax Error] - %s: '%s' (ln:%d, pos:%d):\n" % (error, token.value, pos[0] + 1, pos[1])
            error_message += getln(pos, len(token.value))
            if not isinstance(params[1], list):
                error_message += "\n\nExpected: '%s'" % params[1]
            code_error = SycCompileError(error_message)
    elif type == "semantic_error" or type == "package_error":
        name_dict = {"semantic_error": "Semantic Error", "package_error": "Package Error"}
        name = name_dict[type]
        if isinstance(params, Token):
            pos = get_position(params.ndx)
            error_message += "[%s] - %s, '%s' (ln:%d, pos:%d):\n" % (name, error, params.value, pos[0] + 1, pos[1])
            error_message += getln(pos, len(params.value))
            code_error = SycCompileError(error_message)
        elif isinstance(params, str):
            code_error = SycCompileError("[%s] - %s" % (name, error))
        else:
            params = unparse(params)
            pos = get_position(params[0].ndx)
            end_pos = get_position(params[-1].ndx)
            error_message += "[%s] - %s (ln:%d, pos:%d):\n" % (name, error, pos[0] + 1, pos[1])
            error_message += code.split("\n")[pos[0]][pos[1] - 1:end_pos[1] + len(params[-1].value)]
            code_error = SycCompileError(error_message)
    raise code_error

