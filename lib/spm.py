# broken

import json
import util
import src.errormodule as er
import src.parser.lexer as lexer
import src.parser.syc_parser as parser
import os


def load_package(name):
    code = open_package(name)
    lx = lexer.Lexer()
    tkns = lx.lex(code)
    p = parser.Parser(tkns)
    return p.parse()


# open a package
def open_package(name):
    index = json.loads(open(util.source_dir + "/lib/package_index.json").read())
    if name in index.keys():
        make_dependency(name, index[name])
        os.chdir(os.path.dirname(index[name]))
        return open(index[name]).read()
    else:
        make_dependency(name.split(".")[0].split("/")[-1], name)
        if os.getcwd() != os.path.dirname(name):
            os.chdir(os.path.dirname(name))
        return open(name).read()


# adds data to a dependency file that will be use later when the compiler is acquiring packages
def make_dependency(name, path):
    if os.getcwd() != os.path.realpath(os.path.dirname(er.main_file)):
        os.chdir(os.path.dirname(er.main_file))
    with open("_build/dependencies.json", "w+") as file:
        if name in json.loads(file.read()):
            er.throw("package_error", "Unable to import package.", name)
        json.dump({name: path}, file)
        file.close()
