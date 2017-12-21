import re
import util


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
        self.command_templates = [r"\bset_path\b", r"\bdebug\b", r"\broot\b", r"\binstall\b", r"\bdel\b", r"\bi\b", r"\bo\b", r"\br\b", r"\bu\b", r"\bv\b"]

    @staticmethod
    def get_type(token_str):
        clean_templates = ["set_path", "debug", "root", "install", "del", "i", "v", "r", "u", "o"]
        if any(x == token_str for x in clean_templates):
            return Token("Command", token_str)
        elif re.match("--\w+", token_str):
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
            token_ndxs = dict(zip([x.start() for x in ndxs], matches))
        regexes = [r"--\w+", "/\w+", "[^ ]+"]
        for regex in regexes:
            matches = re.findall(regex, string)
            ndxs = re.finditer(regex, string)
            token_ndxs = dict(zip([x.start() for x in ndxs], matches))
        nums = [x for x in token_ndxs]
        nums.sort()
        return [self.get_type(token_ndxs[x]) for x in nums]

    def parse_cmd(self, string):
        tokens = self.tokenize(string)
        if tokens[0].type != "Command":
            raise(util.CustomException("Unable to match argument '%s' with command." % tokens[0].value))
        cmd_array = []
        current_command = Command(tokens[0].value)
        tokens.pop(0)
        for token in tokens:
            if token.type == "Command":
                cmd_array.append(current_command)
                current_command = Command(token.value)
            elif token.type == "Modifier":
                current_command.modifiers.append(token.value)
            elif token.type == "Specifier":
                current_command.specifiers.append(token.value)
            else:
                current_command.parameters.append(token.value)
        cmd_array.append(current_command)
        self.commands = cmd_array


def get_cmd_obj(in_str):
    ip_obj = InputObject()
    ip_obj.parse_cmd(in_str)
    return ip_obj
