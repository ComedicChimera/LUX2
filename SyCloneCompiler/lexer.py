import re
import errormodule as er

class Lexer():
    def __init__(self):
        #creates a holder for the inital code
        self.code = ""
        #creates a default array for the tokens
        self.tokens = []
        # provides a set of tokens and their templates
        self.tokenTypes = {
            "STRING_LITERAL": r'"([^"]*)"',
            "CHAR_LITERAL": r"'([^']*)'",
            "FLOAT_LITERAL": r"\d+\.\d+",
            "INTEGER_LITERAL": r"\d+",
            "COALESCING_OPERATOR": "??",
            "DOLLAR": "$",
            "QUESTION": "?",
            "COLON": ":",
            "COMMA": ",",
            "FLOW_IN": "<<",
            "FLOW_OUT": ">>",
            "NOT_EQUAL": "!=",
            "NEGATE": "!",
            "INCREMENT": "++",
            "DECREMENT": "--",
            "PLUS_EQUALS": "+=",
            "MINUS_EQUALS": "-=",
            "TIMES_EQUALS": "*=",
            "DIVIDE_EQUALS": "/=",
            "MOD_EQUALS": "%=",
            "EXP_EQUALS": "^=",
            "AND": "&&",
            "OR": "||",
            "XOR": "^^",
            "PLUS": "+",
            "MINUS": "-",
            "TIMES": "*",
            "DIVIDE": "/",
            "EXPONENT": "^",
            "MODULUS": "%",
            "EQUALS": "==",
            "GREATER_EQUALS": ">=",
            "LESS_EQUALS": "<=",
            "LAMBDA_OPERATOR": "=>",
            "ASSIGNMENT_OPERATOR": "=",
            "SEMICOLON": ";",
            "STRAIGHT": "|",
            "OPEN_PAREN": "(",
            "CLOSE_PAREN": ")",
            "OPEN_CURLY": "{",
            "CLOSE_CURLY": "}",
            "OPEN_BRACKET": "[",
            "CLOSE_BRACKET": "]",
            "ENIGMA_OPERATOR": "<\\",
            "GREATER_THAN": ">",
            "LESS_THAN": "<",
            "CONST_OPERATOR": "&",
            "AT_OPERATOR": "@",
            "INT_TYPE": "~int~",
            "IF": "~if~",
            "ELSE": "~else~",
            "STRING_TYPE": "~str~",
            "FLOAT_TYPE": "~float~",
            "FUNC": "~func~",
            "THEN": "~then~",
            "RETURN": "~return~",
            "RT_VOID": "~void~",
            "NULL": "~null~",
            "WHEN": "~when~",
            "YIELD": "~yield~",
            "CHAR_TYPE": "~char~",
            "MODULE": "~module~",
            "STRUCT": "~struct~",
            "BEHAVIOR": "~behavior~",
            "CLASS": "~class~",
            "REQUIRED": "~required~",
            "LET": "~let~",
            "BOOL_TYPE": "~bool~",
            "LIST_TYPE": "~list~",
            "DICTIONARY_TYPE": "~dict~",
            "PROTECTED": "~protected",
            "PUBLIC": "~public~",
            "PRIVATE": "~private~",
            "GLOBAL_SCOPE": "~global~",
            "LOCAL_SCOPE": "~local~",
            "THIS": "~this~",
            "EXTERN_TYPE": "~extern~",
            "NEW": "~new~",
            "ERROR_HANDLER": "~onerror~",
            "THROW": "~throw~",
            "EMPTY": "~pass~",
            "WHILE": "~while~",
            "FOR": "~for~",
            "IN": "~in~",
            "REPEAT": "~repeat~",
            "MANAGER": "~manager~",
            "AS": "~as~",
            "WITH": "~with~",
            "SET": "~set~",
            "BYTE_TYPE": "~byte~",
            "AWAIT": "~await~",
            "ACTIVE_TYPE": "~active~",
            "ASYNC" :"~async~",
            "PASSIVE_TYPE": "~passive~",
            "CALL_OBJ": "~call~",
            "ASSEMBLER": "~assembler~",
            "LAMBDA": "~lambda~",
            "BOOL_LITERAL": r"(?i)~true~|~false~",
            "IDENTIFIER": r"[_a-zA-Z]+\w*"
        }

    def Lex(self, code):
        er.Log("Locating Tokens", 1)
        phrases = {}
        #removes comments and whitespace
        code = code.replace("\n", "~").replace("\t", "~")
        code = self.ClearComments(code)
        #checks for all direct matches
        counter = 0
        for type in self.tokenTypes:
            counter += 1
            regex = ["IDENTIFIER", "CHAR_LITERAL", "STRING_LITERAL", "BOOL_LITERAL", "INTEGER_LITERAL", "FLOAT_LITERAL"]
            if(type in regex):
                rx = re.compile(self.tokenTypes[type])
                tokens = rx.findall(code)
                if (len(tokens) > 0):
                    for item in tokens:
                        ndx = code.find(item)
                        phrases[ndx] = (item.strip("~"), type)
                        code = code.replace(item, "~" * len(item), 1)
            else:
                code = code.replace(" ", "~")
                rx = re.compile(re.escape(self.tokenTypes[type]))
                tokens = rx.findall(code)
                if (len(tokens) > 0):
                    for item in tokens:
                        ndx = code.find(item)
                        phrases[ndx] = (item.strip("~"), type)
                        code = code.replace(item, "~" * len(item), 1)
            if(counter > 3):
                code = code.replace(" ", "~")
        if(code != "~" * len(code)):
            er.Log("Invalid Token", 3)
        #sorts them in order
        numbers = [x for x in phrases]
        numbers.sort()
        phraseList = [phrases[x] for x in numbers]
        return phraseList

    def ClearComments(self, code):
        # removes all inline comments
        inlineComments = re.findall("//.+", code)
        for item in inlineComments:
            code = code.replace(item, "")
        # removes all multiline comments
        multilineComments = re.findall("/\*.+\*/", code)
        for item in multilineComments:
            code = code.replace(item, "", 1)
        return code