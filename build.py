import os

import syc.parser.syc_parser as parser
from syc.parser.ASTtools import ASTNode
import syc.icg.generate as generate

import errormodule
import syc.parser.lexer as lexer
import util
from lib.package_manager import get


# dictionary to hold used imports
imports = {

}

# possible command modifiers
MODIFIERS = ['--sandbox']


def build(args):
    util.build_file = ''
    # modifiers
    mods = []
    for arg in args:
        # if arguments is not a modifier, take as build file
        # if build file is set more than once, fail due to multiple build files
        if arg not in MODIFIERS:
            if util.build_file != '':
                raise util.SyCloneError('Multiple build files specified.')
            util.build_file = arg
        else:
            mods.append(arg)
    # first open and compile the startup file
    # loads all constants into memory
    with open(util.SOURCE_DIR + '/lib/corelib/__init__.sy') as file:
        ast = get_ast(file.read())
    global imports
    # reset imports (free memory)
    imports = {}
    action_tree = generate.generate_tree(ast)
    # TODO optimize action tree
    # TODO convert action tree to llvm code


# parse code to ast with resolved imports
def get_ast(code):
    # lex to tokens
    lx = lexer.Lexer()
    tokens = lx.lex(code)
    # parse to AST
    pr = parser.Parser(tokens)
    ast = pr.parse()
    # get all the imports and the package objects
    return resolve_imports(ast)


# loads in package objects
def resolve_imports(ast):
    # iterate through ast
    for i in range(len(ast.content)):
        item = ast.content[i]
        if isinstance(item, ASTNode):
            # if these is an include statement, process it
            if item.name == 'include_stmt':
                ast.content[i] = load_package(item)
            # recur and continue checking for includes
            else:
                ast.content[i] = resolve_imports(item)
    return ast


# open package from ast
def load_package(include_stmt):
    # package name
    name = ''
    # if it is anonymous
    used = False
    # if it is external
    extern = False
    for item in include_stmt.content:
        if isinstance(item, ASTNode):
            # add suffix to main name
            if item.name == 'dot_id':
                name += ''.join(util.unparse(item))
            # if this sub tree exists, that means the inclusion is used
            elif item.name == 'use':
                used = True
            # if this exists that means that the inclusion is meant to be exported
            elif item.name == 'extern':
                extern = True
        else:
            # get base name
            if item.type == 'IDENTIFIER':
                name = item.value
    # package cannot be used and external
    if used and extern:
        errormodule.throw('package_error', 'Package cannot be both external and anonymous.', include_stmt)
    # prevent redundant imports
    if name in imports:
        code, path = imports[name]
    # if import not redundant, fetch new import
    else:
        # if get fails due to file path not being found
        try:
            code, path = get(name)
        except FileNotFoundError:
            errormodule.throw('package_error', 'Unable to locate package by name \'%s\'.' % name, include_stmt)
            return
        # add to dictionary so it is not imported multiple times
        imports[name] = code, path
    # if working directory needs to be updated
    if path:
        # store cwd
        cwd = os.getcwd()
        # chdir to the parent directory of the file to allow for local importing
        os.chdir(path)
        # get the data necessary
        ast = get_ast(code)
        # change back to cwd
        os.chdir(cwd)
    else:
        # just get the ast, no cwd recursion necessary
        ast = get_ast(code)
    return util.Package(name, extern, used, ast)

