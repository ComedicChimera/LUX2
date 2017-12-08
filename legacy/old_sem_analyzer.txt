from src.ASTtools import ASTNode, Token
from src.errormodule import throw
from src.errormodule import get_tree_string


# default data type class
class DataType:
    def __init__(self):
        self.data_type = ""
        self.pointer = ""


# default Dictionary data type
class DictType(DataType):
    def __init__(self):
        DataType.__init__(self)
        self.key_type = DataType()
        self.value_type = DataType()


# default List data type
class ListType(DataType):
    def __init__(self):
        DataType.__init__(self)
        self.elem_type = DataType()


# evaluates different expressions to get types
class ExpressionEvaluator:
    def __init__(self):
        pass

    # gets a data type from the extension node
    @staticmethod
    def get_type_from_extension(extension):
        return ExpressionEvaluator.get_data_type(extension.content[1].content)

    # given a "types" object, generate a data type object
    @staticmethod
    def get_data_type(content):
        var_type = DataType()
        for item in content:
            if isinstance(item, Token):
                if item.type == "LIST_TYPE":
                    var_type = ListType()
                    var_type.data_type = "LIST_TYPE"
                elif item.type == "DICT_TYPE":
                    var_type = DictType()
                    var_type.data_type = "DICT_TYPE"
                else:
                    var_type.data_type = item.type
            elif item.name == "deref_op":
                var_type.pointer = get_tree_string(item)
            else:
                # handle types and collections
                if item.name == "pure_types":
                    var_type.data_type = item.content[0].type
                elif item.name == "list_modifier":
                    var_type.elem_type = ExpressionEvaluator.get_data_type(item.content[1].content)
                elif item.name == "dict_modifier":
                    var_type.key_type = ExpressionEvaluator.get_data_type(item.content[1].content[0].content)
                    var_type.value_type = ExpressionEvaluator.get_data_type(item.content[1].content[2].content)
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

    # unwraps a tree into a list of its elements
    def unwind(self, tree):
        t_list = []
        for item in tree.content:
            if isinstance(item, Token):
                t_list.append(item)
            else:
                t_list += self.unwind(item)
        return t_list

    # declares a new variable
    def declare(self, name, modifiers, token):
        print(SemanticAnalyzer.symbol_table[self.scope][-1])
        var = Variable(name, modifiers)
        if var.__dict__ not in [x.__dict__ for x in SemanticAnalyzer.symbol_table[self.scope][-1]]:
            SemanticAnalyzer.symbol_table[self.scope][-1].append(var)
        else:
            throw("semantic_error", "Redeclared Identifier", token)

    @staticmethod
    def check_modifiers(modifiers, name):
        used_modifiers = []
        for modifier in modifiers:
            if len(used_modifiers) > 3:
                throw("semantic_error", "Unable to apply contradicting modifiers", modifier)
            if modifiers in used_modifiers:
                throw("semantic_error", "Redundant modifiers", modifier)
            if "." not in name and modifier.type in ["PRIVATE", "PROTECTED"]:
                throw("semantic_error", "Unable to apply access modifier to ungrouped entity.", modifier)
            used_modifiers.append(modifier)

    # the global semantic check function
    def semantic_assert(self, ast, context):
        if context == "variable_decl_stmt":
            if len(ast.content) > 2 and isinstance(ast.content[0], Token):
                name = get_tree_string(ast.content[1])
                var_type = DataType()
                if ast.content[2].name == "extension":
                    var_type = ExpressionEvaluator.get_type_from_extension(ast.content[2])
                self.declare(name, {"data_type": var_type}, ast.content[1])
            elif len(ast.content) > 3 and isinstance(ast.content[0], ASTNode):
                modifiers = self.unwind(ast.content[0])
                name = get_tree_string(ast.content[2])
                self.check_modifiers(modifiers, name)
                var_type = DataType()
                if ast.content[3].name == "extension":
                    var_type = ExpressionEvaluator.get_type_from_extension(ast.content[3])
                self.declare(name, {"data_type": var_type, "modifiers": modifiers}, ast.content[2])
            else:
                throw("semantic_error", "Unable to determine type of variable", ast.content[1])

    # matches a tree to its correct assertion
    def match(self, x):
        if isinstance(x, ASTNode):
            if x.name == "block":
                self.scope += 1
                if self.scope not in SemanticAnalyzer.symbol_table.keys():
                    SemanticAnalyzer.symbol_table[self.scope] = []
                SemanticAnalyzer.symbol_table[self.scope].append([])
                self.evaluate(x)
                self.scope -= 1
            elif x.name in self.semantics:
                if self.scope not in SemanticAnalyzer.symbol_table.keys():
                    SemanticAnalyzer.symbol_table[self.scope] = [[]]
                self.semantic_assert(x, x.name)
            else:
                self.evaluate(x)

    # evaluates an AST
    def evaluate(self, ast):
        for item in ast.content:
            self.match(item)
        return ast


# the main check function
def prove(ast):
    sem = SemanticAnalyzer()
    return sem.evaluate(ast)

