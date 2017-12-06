from src.ASTtools import ASTNode, Token
from src.errormodule import throw
from src.errormodule import get_tree_string


class DataType:
    def __init__(self):
        self.data_type = ""
        self.pointer = ""


class DictType(DataType):
    def __init__(self):
        DataType.__init__(self)
        self.key_type = DataType()
        self.value_type = DataType()


class ListType(DataType):
    def __init__(self):
        DataType.__init__(self)
        self.elem_type = DataType()


class ExpressionEvaluator:
    def __init__(self):
        pass

    @staticmethod
    def get_type_from_extension(extension):
        return ExpressionEvaluator.get_data_type(extension.content[1].content)

    @staticmethod
    def get_data_type(content):
        var_type = DataType()
        for item in content:
            if isinstance(item, Token):
                pass
            elif item.name == "deref_op":
                var_type.pointer = get_tree_string(item)
            else:
                # handle types and collections
                print(content)
        return var_type


class Variable:
    def __init__(self, name, properties):
        self.name = name
        self.properties = properties


class SemanticAnalyzer:
    # global symbol table for the compiler
    symbol_table = {}

    def __init__(self):
        self.scope = 0
        self.semantics = ["variable_decl_stmt", "assignment", "atom"]

    def declare(self, var):
        pass

    def semantic_assert(self, ast, context):
        if context == "variable_decl_stmt":
            if len(ast.content) > 2:
                name = ast.content[1]
                var_type = DataType()
                if ast.content[2].name == "extension":
                    var_type = ExpressionEvaluator.get_type_from_extension(ast.content[2])
                self.declare(name)
            else:
                throw("semantic_error", "Unable to determine type of variable", ast.content[1])

    def match(self, x):
        if isinstance(x, ASTNode):
            if x.name == "block":
                self.scope += 1
                self.evaluate(x)
                self.scope -= 1
            elif x.name in self.semantics:
                self.semantic_assert(x, x.name)
            else:
                self.evaluate(x)

    def evaluate(self, ast):
        for item in ast.content:
            self.match(item)
        return ast


def prove(ast):
    sem = SemanticAnalyzer()
    return sem.evaluate(ast)

