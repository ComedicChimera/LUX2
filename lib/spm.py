import json
import util
import src.errormodule as er
import src.parser.lexer as lexer
import src.parser.syc_parser as parser
import os


imports = {

}


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
        er.file = os.path.abspath(index[name])
        util.chdir(er.file)
        return open(index[name]).read()
    else:
        make_dependency(name.split(".")[0].split("/")[-1], name)
        er.file = os.path.abspath(name)
        util.chdir(er.file)
        print(os.getcwd())
        return open(name).read()


# adds data to a dependency file that will be use later when the compiler is acquiring packages
def make_dependency(name, path):
    util.chdir(er.main_file)
    if name not in imports.keys():
        imports[name] = path
