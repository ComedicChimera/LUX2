import re

code = ""


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


def throw(type, error, params):
    print(type, error, params)
    exit(0)
