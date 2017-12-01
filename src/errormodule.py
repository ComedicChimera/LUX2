import re
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


def throw(type, error, params):
    if type == "syntax_error":
        print("")
        token = params[0]
        pos = get_position(token.ndx)
        print(ConsoleColors.RED + "[Syntax Error] - %s: '%s' (ln:%d, pos:%d):" % (error, token.value, pos[0] + 1, pos[1]))
        print(code.split("\n")[pos[0]])
        print(" " * pos[1], end="")
        print("^" * len(token.value))
        if not isinstance(params[1], list):
            print("\nExpected: '%s'" % params[1])
    exit(0)
