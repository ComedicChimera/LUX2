import re

code = ""


def throw(type, error, params):
    if type == "lexerror":
        if params == "\"" or params == "\'":
            return
        temp_code = code
        ndx = temp_code.index(params)
        t_code = code.replace("\t", "").split("\n")
        count = 0
        ln_count = 0
        for item in t_code:
            count += len(item)
            if count > ndx + len(params):
                ln_count -= 1
                break
            ln_count += 1
        print("\n" + ConsoleColors.RED + error + " (\'" + params + "\') [ln:" + str(ln_count) + " - " + str(t_code[ln_count].index(params) + 1) + "]:")
        print(t_code[ln_count])
        print(" " * t_code[ln_count].index(params) + "^" * len(params))
    elif type == "syntax_error":
        spaces = re.findall(r" ", code)
        params[0] += len(spaces)
        end_pos = params[0] + params[1]
        split_code = code.split("\n")
        i = 0
        length = 0
        for item in split_code:
            if params[0] >= length and end_pos <= length + len(item):
                break
            i += 1
            length += len(item)
        print("\n" + ConsoleColors.RED + error + " (\'" + params + "\') [ln:" + str(i) + " - " + str(params[0]) + "]:")
        print(split_code[i])
        print(" " * (params[0] - length) + "^" * params[1])
    exit(0)


class CustomException(Exception):
    pass


class ConsoleColors:
    MAGENTA = '\033[35m'
    BLUE = '\033[34m'
    GREEN = '\033[32m'
    YELLOW = '\033[93m'
    RED = '\033[31m'
    WHITE = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'