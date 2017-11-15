# cmd parser is broken
import re


class Command:
    def __init__(self, name):
        self.name = name
        self.parameters = []
        self.specifiers = []
        self.modifiers = []


class Token:
    def __init__(self, type, value):
        self.value = value
        self.type = type

class InputObject:
    def __init__(self):
        self.commands = []
        self.command_templates = [r"\bdebug\b", r"\broot\b", r"\binstall\b", r"\bdel\b", r"\bi\b", r"\bo\b", r"\br\b", r"\bu\b", r"\bv\b"]

    def get_type(self, token_str):
        for template in self.command_templates:
            if re.match(template, token_str):
                return Token("Command", token_str)
        if re.match("--\w+", token_str):
            return Token("Modifier", token_str)
        elif re.match("/\w+", token_str):
            return Token("Specifier", token_str)
        else:
            return Token("Parameter", token_str)

    def tokenize(self, string):
        token_ndxs = {}
        for template in self.command_templates:
            matches = re.findall(template, string)
            ndxs = re.finditer(template, string)
            token_ndxs = dict(zip(ndxs, matches))
        regexes = [r"--\w+", "/\w+", "[^ ]+"]
        for regex in regexes:
            matches = re.findall(regex, string)
            ndxs = re.finditer(regex, string)
            token_ndxs = dict(zip(ndxs, matches))
        nums = [x for x in token_ndxs]
        nums.sort()
        return [self.get_type(token_ndxs[x]) for x in nums]

    def parse_cmd(self, string):
        tokens = self.tokenize(string)


def get_cmd_obj(in_str):
    ip_obj = InputObject()
    ip_obj.parse_cmd(in_str)
    return ip_obj
