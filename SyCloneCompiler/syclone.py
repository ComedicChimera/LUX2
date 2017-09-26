import subprocess
from inspect import signature
import os
import lexer
import syc_parser
import errormodule as er

#the main application
class Console:
    #sets up the default commands dictionary
    def __init__(self):
        self.commands = {
            "i": self.In,
            "o": self.Out,
            "log": self.Log,
            ".": self.Run,
            "install": self.Install,
            "u": self.Update
        }
        self.currentFile = ""
        self.fileType = ""

    def Install(self):
        pass

    def Update(self):
        pass

    def Out(self):
        pass

    def Log(self, level):
        if(level == "debug"):
            er.log_level = 0
        elif(level == "status"):
            er.log_level = 1
        elif(level == "warn"):
            er.log_level = 2
        elif(level == "fatal"):
            er.log_level = 3
        else:
            raise CustomException("Invalid Log Level.")

    #brings in a file
    def In(self, path):
        if(path.endswith(".sy") or path.endswith(".txt")):
            self.fileType = "source"
        elif(path.endswith(".sbc")):
            self.fileType = "bytecode"
        elif(path.endswith(".syo")):
            self.fileType = "object"
        else:
            raise CustomException("Invalid file type.")
        with open(path) as fileObject:
            for item in fileObject:
                self.currentFile += item

    #runs a file
    def Run(self):
        if(self.fileType == "source"):
            self.Compile(" " + self.currentFile)
        else:
            raise NotImplementedError

    #gets input from user
    def GetInput(self):
        os.chdir("C:/Users/forlo/Desktop/Coding/Python/SyCloneCompiler")
        command = ""
        while(command != "exit"):
            #try:
                print(bcolors.MAGENTA + "SYC_VCP@x64 " + bcolors.GREEN + os.getcwd() + bcolors.YELLOW + " ~\n" + bcolors.WHITE + "$ ", end="")
                command = input("")
                # if is a syc command, the syc parser will handle it
                if (command.startswith("syc ")):
                    self.EvaluateCommand(command)
                #test if command is cd and revise current dir to compensate
                elif(command[:2] == "cd"):
                    os.chdir(command[3:])
                #else it will echo to console and print response
                elif (command != "exit"):
                    output = subprocess.check_output(command, shell=True)
                    print(str(output).replace("b'", "").replace("\\n", "\n").replace("\\r", "\r")[:len(output) - 1])
            #except Exception as e:
                #print(bcolors.RED + str(e))
                print("\n")

    #splits the command into its parts and executes it
    def EvaluateCommand(self, command):
        command = command.strip("syc ")
        items = command.split(" ")
        args = []
        for item in items:
            if(item in self.commands.keys()):
                args.append(("cmd", item))
            else:
                args.append(("arg", item))
        reqParams = False
        currentFunc = ""
        for item in args:
            if(item[0] == "cmd"):
                if(reqParams):
                    raise(CustomException("Commands arguments required."))
                else:
                    if (len(signature(self.commands[item[1]]).parameters) > 0):
                        reqParams = True
                        currentFunc = item[1]
                    else:
                        self.commands[item[1]]()
                        reqParams = False
            else:
                if(not reqParams):
                    raise(CustomException("No arguments necessary."))
                else:
                    self.commands[currentFunc](item[1])
                    reqParams = False


    def Compile(self, code):
        lx = lexer.Lexer()
        tokens = lx.Lex(code)
        er.Log("Lexical Analysis Complete", 1)
        er.Log(tokens, 0)
        pr = syc_parser.Parser()
        sepT = pr.Buffer(tokens)
        tree = pr.Parse(sepT)
        er.Log("Parsing Complete", 1)
        er.Log(tree, 0)
        # get parse tree

class CustomException(Exception):
    pass

class bcolors:
    MAGENTA = '\033[35m'
    BLUE = '\033[34m'
    GREEN = '\033[32m'
    YELLOW = '\033[93m'
    RED = '\033[31m'
    WHITE = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

cn = Console()
cn.GetInput()