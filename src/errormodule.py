import re
from util import *

code = ""


def throw(type, error, params=""):
    if type == "syntax_error":
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
