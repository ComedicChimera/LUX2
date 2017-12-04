import re
from src.ASTtools import Token
import json
import util
import src.errormodule as er


class Lexer:
    def __init__(self):
        # creates a holder for the inital code
        self.code = ""
        # creates a default array for the tokens
        self.tokens = []
        # provides a set of tokens and their templates
        self.tokenTypes = json.loads(open(util.source_dir + "/src/config/tokens.json").read())

    def lex(self, code):
        phrases = {}
        # removes comments and whitespace
        code = self.clear_comments(code)
        er.code = code
        # checks for all direct matches
        for token in self.tokenTypes:
            matches = re.finditer(re.compile(self.tokenTypes[token]), code)
            for match in matches:
                if match.group(0) != "" and match.start() not in phrases.keys():
                    phrases[match.start()] = Token(token, match.group(0), match.start())
                    code = re.sub(self.tokenTypes[token], " " * len(match.group(0)), code, 1)
        # sorts them in order
        numbers = [x for x in phrases]
        numbers.sort()
        phrase_list = [phrases[x] for x in numbers]
        return phrase_list

    @staticmethod
    def clear_comments(code):
        # removes all multi-line comments
        multi_line_comments = re.findall(re.compile("/\*.*\*/", re.MULTILINE | re.DOTALL), code)
        for item in multi_line_comments:
            code = code.replace(item, "", 1)
        single_line_comments = re.findall(re.compile("//.*\n*"), code)
        for item in single_line_comments:
            code = code.replace(item, "", 1)
        return code
