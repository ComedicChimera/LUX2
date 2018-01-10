import json
import re

import src.errormodule as er
import util
from src.parser.ASTtools import Token


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
                # checks to make sure all char literals are valid
                if token == "CHAR_LITERAL":
                    self.check_char(match.group(0)[1:len(match.group(0)) - 1], match.start())
                if match.group(0) != "" and match.start() not in phrases.keys():
                    phrases[match.start()] = Token(token, match.group(0), match.start())
                    code = re.sub(self.tokenTypes[token], " " * len(match.group(0)), code, 1)
        # sorts them in order
        numbers = [x for x in phrases]
        numbers.sort()
        phrase_list = [phrases[x] for x in numbers]
        self.check_unmatched(code)
        return phrase_list

    @staticmethod
    def clear_comments(code):
        # removes all multi-line comments
        multi_line_comments = re.findall(re.compile("/\*.*\*/", re.MULTILINE | re.DOTALL), code)
        for item in multi_line_comments:
            lines = item.split("\n")
            for line in range(len(lines)):
                lines[line] = " " * len(lines[line])
            new_comment = "\n".join(lines)
            code = code.replace(item, new_comment, 1)
        single_line_comments = re.findall(re.compile("//.*\n*"), code)
        for item in single_line_comments:
            code = code.replace(item, "\n" + (" " * (len(item) - 2)) + "\n", 1)
        return code

    @staticmethod
    def check_char(char, ndx):
        slash_chars = ["\\n", "\\t", "\\r", "\\\\"]
        if len(char) > 1:
            if char not in slash_chars:
                er.throw("lex_error", "Invalid char literal", [char, ndx])

    @staticmethod
    def check_unmatched(code_str):
        unmatched = re.finditer(r"[^\s]", code_str)
        for item in unmatched:
            er.throw("lex_error", "Invalid identifier name", [item.group(0), item.start()])



