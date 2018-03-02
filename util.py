import os


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

source_dir = os.path.dirname(os.path.realpath(__file__))

version = "0.0.1"


def chdir(path):
    print(path)
    directory = os.path.dirname(os.path.abspath(path)).split('\\')
    directory.pop()
    directory = "\\".join(directory)
    print(directory)
    os.chdir(directory)
