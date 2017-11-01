import re
from util import *


class DirectiveParser:
    def __init__(self):
        pass

    @staticmethod
    def include(str_literal):
        pass

    @staticmethod
    def using(str_literal):
        pass

    @staticmethod
    def define(str_literal):
        pass

directives = {
    "include": DirectiveParser.include,
    "using": DirectiveParser.using,
    "define": DirectiveParser.define
}


class Directive:
    def __int__(self, direct, params):
        self.direct = direct
        self.params = params


def match_dir(directive):
    pure_dir = directive[1:len(directive)]
    split_directive = pure_dir.split(" ")
    true_dir = split_directive[0]
    split_directive.pop(0)
    return Directive(true_dir, split_directive)


def main(code):
    dirs = re.findall("#[^;];", code)
    dir_obj_queue = []
    for item in dirs:
        dir_obj_queue.append(match_dir(item))
    has_package_decl = False
    for item in dir_obj_queue:
        if item.direct == "package" and not has_package_decl:
            has_package_decl = True
        elif item.direct != "package" and has_package_decl:
            directives[item.direct] = item.params
        else:
            raise CustomException("Invalid directive.")
