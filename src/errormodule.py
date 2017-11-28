import re
from util import *

code = ""


def throw(type, error, params=""):
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
        print("\nLex Error: " + ConsoleColors.RED + error + " (\'" + params + "\') [ln:" + str(ln_count) + " - " + str(t_code[ln_count].index(params) + 1) + "]:")
        print(t_code[ln_count])
        print(" " * t_code[ln_count].index(params) + "^" * len(params))
    elif type == "syntax_error":
        error = str(error)
        token = re.search("\'[^\']+\'", error).group()
        line = str(int(re.search("\d+", re.search("line \d+,", error).group()).group()) - 1)
        position = re.search("\d+", re.search("column \d+.", error).group()).group()
        print(ConsoleColors.RED + "Unexpected Token: " + token + " at [ln:" + line + "," + position + "]")
        l_line = code.split("\n")[int(line) - 1]
        if l_line == '':
            print(l_line[1:])
        else:
            print(code[1:])
        print((" " * (int(position) - 1)) + ("^" * (len(token) - 2)))
        print("\nExpected: " + error.split("\n")[1].split("[")[1].split(",")[0] + ConsoleColors.WHITE)
    exit(0)
