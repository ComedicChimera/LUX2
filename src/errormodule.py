import re
from util import *

code = ""


def throw(type, error, params):
    if type == "syntax_error":
        token = params[0]
        print(ConsoleColors.RED + "[Syntax Error]: %s, '%s' [ndx:%d]\n\nExpected: '%s'." % (error, token.value, token.ndx, params[1]))
    exit(0)
