import subprocess
from inspect import signature
import os
import src.lexer as lexer
import src.syc_parser as syc_parser
import src.errormodule as er
import src.ASTtools as ASTtools
import src.semantic_analyzer as sem
from util import *
import cmd


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
            "bug": self.debug()
        }

        self.currentFile = ""
        self.fileType = ""

    def debug(self):
        pass

    # returns the current version of SyClone
    @staticmethod
    def get_version():
        print("SyClone Version: " + version)

    def install(self):
        pass

    def update(self):
        pass

    def out_func(self):
        pass

    # brings in a file
    def in_func(self, params):
        if len(params) != 1:
            raise(CustomException("Function IN does not except more that one path."))
        path = params[0]
        if path.endswith(".sy") or path.endswith(".txt"):
            self.fileType = "source"
        else:
            raise CustomException("Invalid file type.")
        with open(path) as fileObject:
            for item in fileObject:
                self.currentFile += item

    # runs a file
    def run(self):
        if self.fileType == "source":
            self.compile(" " + self.currentFile, False)
        else:
            raise NotImplementedError

    # gets input from user
    def get_input(self):
        command = ""
        while command != "exit":
            # try:
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
            # except Exception as e:
                # print(bcolors.RED + str(e))
                print("\n")

    # splits the command into its parts and executes it
    def evaluate_command(self, command):
        # removes unnecessary content
        command = command.strip("syc ")
        # converts cmd into an object
        cmd_obj = cmd.get_cmd_obj(command)
        # iterates through and executes each command
        for item in cmd_obj.commands:
            # if it is not a known command, it will raise an exception
            # NOTE: if this evaluates to true, the cmd object parser and the executor may be out of sync (version wise)
            if item.name not in self.commands.keys():
                raise(CustomException("Unknown Command."))
            # checks to see if right numbers of params were passed (none or some)
            if len(item.parameters) > 0 and len(signature(self.commands[item.name]).parameters) > 0:
                self.commands[item.name](item.parameters)
            elif len(item.parameters) == 0 and len(signature(self.commands[item.name]).parameters) == 0:
                self.commands[item.name]()
            else:
                # throws appropriate error if not
                if len(item.parameters) > len(signature(self.commands[item.name]).parameters):
                    raise(CustomException("Too many parameters for function %s!" % item.name))
                else:
                    raise(CustomException("Too few parameters for function %s!" % item.name))

    # main compile function
    def compile(self, code, generate_file):
        print(ConsoleColors.BOLD + "Starting Compiler..." + ConsoleColors.WHITE)
        print("\n", end="")
        # run preprocessor
        print("Running Preprocessor...\n")
        p_code = code
        self.analyze(p_code, generate_file)

    # gets semantically valid AST and catches compile time errors
    @staticmethod
    def analyze(code, generate_file):
        # sets error module code
        er.code = code
        # runs lexer
        print(ConsoleColors.BLUE + "Lexing..." + ConsoleColors.WHITE)
        lx = lexer.Lexer()
        tokens = lx.lex(code)
        print((ConsoleColors.YELLOW + "Found {0} tokens." + ConsoleColors.WHITE).format(len(tokens)))
        print("\n", end="")
        # runs ll(1) parser
        print(ConsoleColors.BLUE + "Parsing..." + ConsoleColors.WHITE)
        pr = syc_parser.Parser()
        tree = pr.parse(tokens)
        print(ConsoleColors.YELLOW + "Generated AST." + ConsoleColors.WHITE)
        print(tree)
        # cleans tree
        tree.content = ASTtools.resolve_ast(tree.content)
        # semantic analysis
        print(ConsoleColors.BLUE + "Running semantic analysis on AST." + ConsoleColors.WHITE)
        sem_valid_obj = sem.sem_analyze(tree)
        # generates output file architecture
        if generate_file:
            os.mkdir("_build")
            os.mkdir("_build/bin")
            os.mkdir("_build/debug")
            os.mkdir("_build/bin/sy_cache")
            with open("_build/bin/sy_cache/tokens.json", "w+") as file:
                file.write(tokens)
                file.close()
            with open("_build/bin/sy_cache/ast.json", "w+") as file:
                file.write(tree)
                file.close()
        return sem_valid_obj

cn = Console()
cn.get_input()
