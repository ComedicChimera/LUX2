import re


class Command:
    def __init__(self, name):
        self.name = name
        self.parameters = []
        self.specifiers = []
        self.modifiers = []


class InputObject:
    def __init__(self):
        self.commands = []
        self.command_templates = ["debug", "root", "install", "del", "i", "o", "r", "u", "v"]

    @staticmethod
    def parse_components(string):
        results = list()
        results.append(re.findall("--\\w+", string))
        results.append(re.findall("/\\w+", string))
        for item in results[0]:
            string = string.replace(item, "")
        for item in results[1]:
            string = string.replace(item, "")
        results.append(re.findall("[\\w.]+", string))
        return results

    def parse_cmd(self, string):
        cmd_components = []
        for template in self.command_templates:
            matches = re.findall(re.escape(template), string)
            for match in matches:
                if len(string.split(match)) > 1:
                    cmd_components.append(string.split(match)[1])
                else:
                    cmd_components.append(string.split(match)[0])
                self.commands.append(Command(match))
                string = string.replace(match, "")
        for i in range(len(self.commands)):
            result = self.parse_components(cmd_components[i])
            self.commands[i].parameters = result[2]
            self.commands[i].specifiers = result[1]
            self.commands[i].modifiers = result[0]


def get_cmd_obj(in_str):
    ip_obj = InputObject()
    ip_obj.parse_cmd(in_str)
    return ip_obj
