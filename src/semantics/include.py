import util
import json
import src.parser.lexer as lexer
import src.parser.syc_parser as parser
import src.errormodule as er

includes = []

# TODO update prefix
load_prefix = ''


def include(file):
    if file == '__application__':
        return load_file(util.main_file)
    index = json.load(open(util.source_dir + '/lib/package_index.json'))
    if file in index.keys():
        return load_file(util.source_dir + '/lib/' + index[file])
    else:
        return load_file(load_prefix + file + '.sy')


def load_file(path):
    er.file = path
    content = open(path).read()
    includes.append(path)
    lx = lexer.Lexer()
    tokens = lx.lex(content)
    p = parser.Parser(tokens)
    ast = p.parse()
    return [ast, path]
