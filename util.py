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


def set_source_dir(path):
    global source_dir
    source_dir = path

source_dir = "C:/Users/forlo/Desktop/Coding/SyClone"
version = "0.0.1"
