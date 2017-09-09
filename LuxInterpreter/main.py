import subprocess
import re
from inspect import signature

class Interpreter():
    def __init__(self):
        #creates a holder for the inital code
        self.code = ""
        #creates a default array for the tokens
        self.tokens = []
        # provides a set of tokens and their templates
        self.tokenTypes = {
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
            "LAMBDA": "=>",
            "ASSIGNMENT_OPERATOR": "=",
            "SEMICOLON": ";",
            "STRAIGHT": "|",
            "OPEN_PAREN": "(",
            "CLOSE_PAREN": ")",
            "OPEN_CURLY": "{",
            "CLOSE_CURLY": "}",
            "OPEN_BRACKET": "[",
            "CLOSE_BRACKET": "]",
            "GREATER_THAN": ">",
            "LESS_THAN": "<",
            "INT_TYPE": "~int~",
            "IF": "~if~",
            "ELSE": "~else~",
            "STRING_TYPE": "~string~",
            "FLOAT_TYPE": "~float~",
            "FUNC": "~func~",
            "VAR": "~var~",
            "RETURN": "~return~",
            "RT_VOID": "~void~",
            "CHAR_TYPE": "~char~",
            "MODULE": "~module~",
            "STRUCT": "~struct~",
            "BEHAVIOR": "~behavior~",
            "CLASS": "~class~",
            "REQUIRED": "~required~",
            "LET": "~let~",
            "STATIC": "~static",
            "BOOL_TYPE": "~bool~",
            "TRUE": "~true~",
            "FALSE": "~false~",
            "LIST_TYPE": "~list~",
            "DICTIONARY_TYPE": "~dict~",
            "PROTECTED": "~protected",
            "PUBLIC": "~public~",
            "PRIVATE": "~private~",
            "GLOBAL_SCOPE": "~global~",
            "LOCAL_SCOPE": "~local~",
            "THIS": "~this~",
            "EVENT": "~event~",
            "EXTERN_TYPE": "~extern~",
            "OUT": "~out~",
            "NEW": "~new~",
            "ERROR_HANDLER": "~onerror~",
            "THROW": "~throw~",
            "EMPTY": "~pass~",
            "WHILE": "~while~",
            "FOR": "~for~",
            "IN": "~in~",
            "MANAGER": "~manager~"
        }

    def Interpret(self, code):
        tokens = self.Lex(code)
        print(tokens)
        pr = Parser()
        sepT = pr.Separate(tokens)
        print(sepT)
        for item in sepT:
            pr.Evaluate(item)
        #get parse tree



    def Lex(self, code):
        phrases = {}
        # gets rid of comments
        code = self.ClearComments(code)
        # removes all unnecessary whitespace
        code = code.replace("\n", "~").replace("\t", "~")
        # finds all string literals in code
        strings = re.findall(r'"([^"]*)"', code)
        for item in strings:
            stringText = "\"" + item + "\""
            phrases[code.find(stringText)] = stringText
            code = code.replace(stringText, "~" * len(stringText), 1)
        # finds all char literals in code
        chars = re.findall(r"'([^']*)'", code)
        for item in chars:
            charText = "'" + item + "'"
            phrases[code.find(charText)] = charText
            code = code.replace(charText, "~" * len(charText), 1)
        # replaces whitespace with null-chars
        code = code.replace(" ", "~")
        # finds all direct token matches
        for item in self.tokenTypes.values():
            rx = re.compile(re.escape(item))
            tokens = rx.findall(code)
            for token in tokens:
                ndx = code.find(token)
                phrases[ndx] = token
                code = code.replace(token, "~" * len(token), 1)
        # gets all non-matches
        codeArray = code.split("~")
        codeArray.sort(key=len)
        codeArray.reverse()
        for item in codeArray:
            if (item != "" and item != " "):
                phrases[code.find(item)] = item
                code = code.replace(item, "~" * len(item), 1)
        # matches all tokens and sorts them into order
        for num in range(len(code)):
            if (num in phrases.keys()):
                item = phrases[num]
                # finds all standard matches
                for key in self.tokenTypes.keys():
                    if (self.tokenTypes[key] == item):
                        self.tokens.append((item.strip("~"), key))
                        break
                # classifies irregulars into either string literal, char literal, float literal, integer literal or identifier
                else:
                    if (item[0] == "\"" and item[len(item) - 1] == "\""):
                        self.tokens.append((item.strip("\""), "STRING_LITERAL"))
                    elif (item[0] == "'" and item[len(item) - 1] == "'"):
                        self.tokens.append((item.strip("'"), "CHAR_LITERAL"))
                    else:
                        try:
                            self.tokens.append((str(int(item)), "INTEGER_LITERAL"))
                        except:
                            try:
                                self.tokens.append((str(float(item)), "FLOAT_LITERAL"))
                            except:
                                if (item != " " and item != ""):
                                    self.tokens.append((item.strip(" ").replace("§", ""), "IDENTIFIER"))
        return self.tokens

    def ClearComments(self, code):
        # removes all inline comments
        inlineComments = re.findall("//.+\n", code)
        for item in inlineComments:
            code = code.replace(item, "", 1)
        # removes all multiline comments
        multilineComments = re.findall("\/\*.+\*\/", code)
        for item in multilineComments:
            code = code.replace(item, "", 1)
        return code

class CustomException(Exception):
    pass

class Parser:
    def __init__(self):
        self.tree = []
        self.grammars = {
            "declaration": [["INT_TYPE", "STRING_TYPE", "LET", "VAR", "FLOAT_TYPE", "CHAR_TYPE", "BOOL_TYPE"],"IDENTIFIER","ASSIGNMENT_OPERATOR","expr","SEMICOLON"]

        }

        self.expressions = {
            "cond_expr": self.EvalCond,
            "ari_expr": self.EvalAri,

        }

    def EvalAri(self, tokens):
        pass

    def CheckForSubG(self, tokens):
        types = []
        for item in tokens:
            types.append(item[1])
        while "OPEN_PAREN" in types:
            oNdx = 0
            cNdx = 0
            counter = 0
            for item in tokens:
                if (item[1] == "OPEN_PAREN"):
                    oNdx = counter
                elif (item[1] == "CLOSE_PAREN"):
                    cNdx = counter
                    subG = self.EvalSubGrammar(tokens[oNdx:cNdx + 1], ["ari_expr"])
                    if (subG != ""):
                        tempTokens = []
                        counter = 0
                        hasAddedSubG = False
                        for curItem in tokens:
                            if (oNdx <= counter <= cNdx):
                                if (hasAddedSubG):
                                    pass
                                else:
                                    tempTokens.append(subG)
                                    hasAddedSubG = True
                            else:
                                tempTokens.append(curItem)
                        print(tempTokens)
                        tokens = tempTokens
        return tokens

    def EvalCond(self, tokens):
        print(tokens)
        tokens = self.CheckForSubG(tokens)
        cTCount = 0
        nTCount = 0
        condTokens = [ "GREATER_THAN", "LESS_THAN", "LESS_EQUALS", "GREATER_EQUALS", "EQUALS", "AND", "OR", "XOR", "NEGATE"]
        numTokens = ["INTEGER_LITERAL", "FLOAT_LITERAL", "BOOL_LITERAL", "STRING_LITERAL", "CHAR_LITERAL", "IDENTIFIER"]
        for token in tokens:
            if(token[1] in condTokens):
                cTCount += 1
            elif(token[1] in numTokens):
                nTCount += 1
            else:
                pass
                #evaluate for subgrammars
        if(cTCount == nTCount - 1):
            print("debug")
            return((True, self.BuildBranch("Conditional", tokens)))
        else:
            return((False, ""))

    #check for subgrammars
    def EvalSubGrammar(self, types, acceptableSub):
        for grammar, func in self.expressions:
            if(grammar in acceptableSub):
                sub = func(types)
                if(sub[0]):
                    return sub[1]
        return ""

    #-----------------------------------------------------------------------#

    #converts a grammar to a tree node
    def BuildBranch(self, type, tokens):
        pass

    #splits the tokens in statement groups
    def Separate(self, tokens):
        splitTokens = []
        tokenGroup = []
        for token in tokens:
            if(token == (";","SEMICOLON") or token == ("}", "CLOSE_CURLY") or token == ("{", "OPEN_CURLY")):
                tokenGroup.append(token)
                splitTokens.append(tokenGroup)
                tokenGroup = []
            else:
                tokenGroup.append(token)
        return splitTokens

    #gets the grammar for each to tokens set
    def Evaluate(self, currentTokens):
        grammar = self.Compare(currentTokens)
        if (grammar[0] == True):
            # build tree
            print(grammar[1])
        else:
            # throw error
            print("Invalid grammar.")

    #compares the evaluated tokens and gets a grammar for them
    def Compare(self, types):
        for grammar in self.grammars.keys():
            counter = 0
            isValid = True
            try:
                for production in self.grammars[grammar]:
                    if (isinstance(production, list)):
                        if (types[counter][1] not in production):
                            isValid = False
                    elif ("expr" in production):
                        if (production == "expr"):
                            for grammar, func in self.expressions.items():
                                subGrammar = func(types)
                                if(subGrammar[0]):
                                    #replace location in tokens for eval
                                    pass
                        else:
                            exprGrammar = self.expressions[production](types)
                            if(exprGrammar[0]):
                                # replace location in tokens for eval
                                pass
                    else:
                        if (types[counter][1] != production):
                            isValid = False
                    counter += 1
            except Exception as eX:
                print(eX)
                isValid = False
            if(isValid):
                return((True, grammar))
        return ((False, ""))

#the main application
class Console:
    #sets up the default commands dictionary
    def __init__(self):
        self.commands = {
            "-i": self.In,
            "-o": self.Out,
            "-log": self.Log,
            "-r": self.Run
        }
        self.currentFile = ""
        self.fileType = ""

    def Out(self):
        pass

    def Log(self):
        pass

    #brings in a file
    def In(self, path):
        if(path.endswith(".lx") or path.endswith(".txt")):
            self.fileType = "source"
        elif(path.endswith(".lbc")):
            self.fileType = "bytecode"
        elif(path.endswith(".lo")):
            self.fileType = "object"
        else:
            raise CustomException("Invalid file type.")
        with open(path) as fileObject:
            for item in fileObject:
                self.currentFile += item

    #runs a file
    def Run(self):
        if(self.fileType == "source"):
            itr = Interpreter()
            itr.Interpret(self.currentFile)
        else:
            raise NotImplementedError

    #gets input from user
    def GetInput(self):
        command = ""
        while(command != "exit"):
            command = input("")
            #if is a lux command, the lux parser will handle it
            if(command.startswith("lux ")):
                self.EvaluateCommand(command)
            #else it will echo it to the command prompt and print the response
            elif(command != "exit"):
                output = subprocess.check_output(command, shell=True)
                print(str(output).replace("b'", "").replace("\\n", "\n").replace("\\r", "\r"))

    #splits the command into its parts and executes it
    def EvaluateCommand(self, command):
        i = 0
        #catches all arguments
        args = re.findall(r'"([^"]*)"', command)
        for item in args:
            command = command.replace("\"" + item + "\"", "")
        #trims lux of off command before splitting begins
        command = command[4:]
        #splits and stores all desired commands
        cmds = command.split(" ")
        try:
            cmds.remove("")
        except:
            pass
        #executes command in order
        try:
            for cmd in cmds:
                #determines if command takes arguments or not
                if (len(signature(self.commands[cmd]).parameters) > 0):
                    self.commands[cmd](args[i])
                    i += 1
                else:
                    self.commands[cmd]()
        except:
            raise CustomException("Invalid Command.")

try:
    cn = Console()
    cn.GetInput()
except Exception as e:
    print(e)