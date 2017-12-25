import re

from src.parser.ASTtools import Token
from util import *

code = ""


def get_position(ndx):
    new_lines = list(re.finditer("\n", code))
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


def println(pos, len_carrots):
    print(code.split("\n")[pos[0]])
    print(" " * pos[1], end="")
    print("^" * len_carrots)


def get_tree_string(tree):
    string = ""
    for item in tree.content:
        if isinstance(item, Token):
            string += item.value + " "
        else:
            string += get_tree_string(item)
    return string


def throw(type, error, params):
    print("")
    if type == "syntax_error":
        if params[0].type == "$":
            token = params[0]
            pos = get_position(token.ndx)
            print(ConsoleColors.RED + "[Syntax Error] - Invalid End of Program, (ln:%d, pos:%d):" % (pos[0] + 1, pos[1]))
            println(pos, len(token.value))
            if not isinstance(params[1], list):
                print("\nExpected: '%s'" % params[1])
        else:
            token = params[0]
            pos = get_position(token.ndx)
            print(ConsoleColors.RED + "[Syntax Error] - %s: '%s' (ln:%d, pos:%d):" % (error, token.value, pos[0] + 1, pos[1]))
            println(pos, len(token.value))
            if not isinstance(params[1], list):
                print("\nExpected: '%s'" % params[1])
    elif type == "semantic_error":
        if isinstance(params, Token):
            pos = get_position(params.ndx)
            print(ConsoleColors.RED + "[Semantic Error] - %s, '%s' (ln:%d, pos:%d):" % (error, params.value, pos[0] + 1, pos[1]))
            println(pos, len(params.value))
        else:
            pos = get_position(params.content[0].ndx)
            print(ConsoleColors.RED + "[Semantic Error] - %s, '%s' (ln:%d, pos:%d):" % (error, get_tree_string(params), pos[0] + 1, pos[1]))
            println(pos, len(get_tree_string(params)))
    exit(0)
