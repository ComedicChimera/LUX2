import re

code = ""

def Throw(type, error, params = ""):
    if(type == "lexerror"):
        ndx = params.index(r"[^~]*")
        print(bcolors.RED + error)
    exit(0)

"""def Log(action, level, end="\n"):
    global log_level
    if (level >= log_level):
        if (level > 2):
            Throw(action)
        else:
            print(action, end=end)"""

class CustomException(Exception):
    pass

class bcolors:
    MAGENTA = '\033[35m'
    BLUE = '\033[34m'
    GREEN = '\033[32m'
    YELLOW = '\033[93m'
    RED = '\033[31m'
    WHITE = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'