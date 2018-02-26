import subprocess
import src.errormodule as er

import src.parser.syc_parser as syc_parser
from src.parser.ASTtools import AST

import cmd
import src.parser.lexer as lexer
from src.semantics.semantic_analyzer import check_ast
from util import *


# the main application
class Console:
    # sets up the default commands dictionary
    def __init__(self):
        self.commands = {
            "i": self.in_func,
            "o": self.out_func,
            "r": self.run,
            "install": self.install,
            "u": self.update,
            "v": self.get_version,
            "bug": self.debug,
        }

        self.currentFile = ""
        self.fileType = ""

    def debug(self):
        pass

    # returns the current version of SyClone
    @staticmethod
    def get_version(cmd_obj):
        if len(cmd_obj.parameters) > 0:
            raise(CustomException("Function GET_VERSION does not except parameters."))
        print("SyClone Version: " + version)

    def install(self, cmd_obj):
        pass

    def update(self, cmd_obj):
        pass

    def out_func(self, cmd_obj):
        pass

    # brings in a file
    def in_func(self, cmd_obj):
        params = cmd_obj.parameters
        if len(params) != 1:
            raise(CustomException("Function IN does not except more that one path."))
        path = params[0]
        if path.endswith(".sy") or path.endswith(".txt"):
            self.fileType = "source"
        else:
            raise CustomException("Invalid file type.")
        er.file = path
        er.main_file = path
        with open(path) as fileObject:
            for item in fileObject:
                self.currentFile += item

    # runs a file
    def run(self, cmd_obj):
        if len(cmd_obj.parameters) > 0:
            raise(CustomException("Function RUN does not except parameters."))
        if self.fileType == "source":
            self.compile(" " + self.currentFile, "")
        else:
            raise NotImplementedError

    # TODO revise function to get input directly from native system command line
    # gets input from user
    def get_input(self):
        command = ""
        while command != "exit":
            print(ConsoleColors.MAGENTA + "SYC_VCP@x64 " + ConsoleColors.GREEN + os.getcwd() + ConsoleColors.YELLOW + " ~\n" + ConsoleColors.WHITE + "$ ", end="")
            command = input("")
            # if is a syc command, the syc parser will handle it
            if command.startswith("syc "):
                self.evaluate_command(command)
            # test if command is cd and revise current dir to compensate
            elif command[:2] == "cd":
                os.chdir(command[3:])
            # else it will echo to console and print response
            elif command != "exit":
                output = subprocess.check_output(command, shell=True)
                print(str(output).replace("b'", "").replace("\\n", "\n").replace("\\r", "\r")[:len(output) - 1])
            print("\n")

    # splits the command into its parts and executes it
    def evaluate_command(self, command):
        # removes unnecessary content
        command = command[4:]
        # converts cmd into an object
        cmd_obj = cmd.get_cmd_obj(command)
        # iterates through and executes each command
        for item in cmd_obj.commands:
            # if it is not a known command, it will raise an exception
            # NOTE: if this evaluates to true, the cmd object parser and the executor may be out of sync (version wise)
            if item.name not in self.commands.keys():
                raise(CustomException("Unknown Command."))
            self.commands[item.name](item)

    # main compile function
    def compile(self, code, output_dir):
        print("Initializing SyClone Compiler [%s] (SycStandard)\n" % version)
        safe_dir = os.getcwd()
        p_code = code
        sc = self.analyze(p_code, output_dir)
        os.chdir(safe_dir)

    # gets semantically valid AST and catches compile time errors
    @staticmethod
    def analyze(code, output_dir=""):
        print("Compiling [          ] (\\)", end="")
        os.chdir(os.path.dirname(er.main_file))
        if not os.path.exists("_build"):
            os.mkdir(output_dir + "_build")
            os.mkdir(output_dir + "_build/bin")
        # gets the tokens from the Lexer
        lx = lexer.Lexer()
        tokens = lx.lex(code)
        print("\rCompiling [#         ] (|)", end="")
        # runs tokens through parser
        parser = syc_parser.Parser(tokens)
        tree = object()
        try:
            tree = parser.parse()
        except RecursionError:
            print(ConsoleColors.RED + "Grammar Error: Left Recursive Grammar Detected.")
            exit(1)
        print("\rCompiling [##        ] (/)", end="")
        # simplify ast
        ast = AST(tree)
        semantic_obj = check_ast(ast)
        print("\rCompiling [####      ] (-)", end="")
        return semantic_obj


cn = Console()
cn.get_input()
