
indent = ""


# token class for ASTs
class Token:
    def __init__(self, type, value, ndx):
        self.type = type
        self.value = value
        self.ndx = ndx

    def pretty(self):
        return "\n" + indent + "Token('%s', '%s')\n" % (self.type, self.value)

    def to_str(self):
        return "Token('%s', '%s')" % (self.type, self.value)


# default AST node class
class ASTNode:
    def __init__(self, name):
        self.name = name
        self.content = []

    def pretty(self):
        global indent
        indent += " "
        pretty_string = "\n" + indent + self.name + ":[\n"
        indent += " "
        for item in self.content:
            pretty_string += item.pretty()
        indent = indent[:len(indent) - 2]
        return pretty_string + "\n" + indent + " ]\n"

    def to_str(self):
        str_string = self.name + ":["
        for item in self.content:
            str_string += item.to_str()
        return str_string + "]"


# class for AST blocks
class ASTBlock:
    def __init__(self, name, header, block):
        self.name = name
        self.header = header
        self.block = block


# class ASTNode statements
class ASTStmt:
    def __init__(self, name, stmt):
        self.name = name
        self.stmt = stmt


# holder class for final AST
class AST:
    def __init__(self, content):
        self.content = content


# removes unnecesary nodes from AST
def reduce(ast):
    content = ast.content
    if len(content) == 1:
        if isinstance(content[0], Token):
            return ast
        else:
            return reduce(content[0])
    else:
        for num in range(len(content)):
            item = content[num]
            if isinstance(item, ASTNode):
                content[num] = reduce(item)
        return ast


# transforms the given not to a block
def convert_to_block(ast):
    content = annotate(ast.content[:len(ast.content) - 1])
    a_block = ast.content[-1]
    block = ASTBlock(ast.name, content, a_block)
    return block


# restructure specific portions of AST to make them more logic (applies all transformers)
def transform(ast):
    pass


# mark AST by type so it is easier to analyze
def annotate(ast):
    for num in range(len(ast.content)):
        item = ast.content[num]
        if isinstance(item, ASTNode):
            if item.name.endswith("block") and item.name != "block" or item.name == "switch_stmt":
                ast.content[num] = convert_to_block(item)
            elif item.name.endswith("stmt") and item.name != "stmt":
                ast.content[num] = ASTStmt(item.name, item.content)
    return ast


# convert parse tree to AST
def get_ast(parse_tree):
    ast = reduce(AST(parse_tree))
    annotated_ast = annotate(ast)
    return annotated_ast
