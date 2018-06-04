from enum import Enum
import syc.icg.modules as modules
from syc.ast.ast import ASTNode, Token


# used to hold template
class Template:
    # template variations
    class TemplateTypes(Enum):
        TYPE = 0
        FUNC = 1
        STRUCT = 2
        ENUM = 3
        MODULE = 4

    def __init__(self, template_type, **kwargs):
        # set the template type
        self.template_type = template_type
        # initialize type template (type)
        if template_type == self.TemplateTypes.TYPE:
            self.type_list = kwargs['type_list']
        # initialize function template (func, async, lambda)
        elif template_type == self.TemplateTypes.FUNC:
            self.parameters = kwargs['parameters']
            self.return_type = kwargs['return_type']
            self.is_async = kwargs['async']
            self.is_lambda = kwargs['lambda']
        # initialize struct & enum template (struct, enum)
        elif template_type in {self.TemplateTypes.STRUCT, self.TemplateTypes.ENUM}:
            self.members = kwargs['members']
        # initialize module template (module)
        elif template_type == self.TemplateTypes.MODULE:
            self.constructor = kwargs['constructor']
            self.members = kwargs['members']
            self.interface = kwargs['interface']

    def compare(self, other):
        # if it is a type template, check if type is in type list
        if self.template_type == self.TemplateTypes.TYPE:
            if other not in self.type_list:
                return False
        # if it is a function template, check if it fulfills all function requirements
        elif self.template_type == self.TemplateTypes.FUNC:
            # all values not specified are None
            if self.parameters and [x.data_type for x in other.parameters] != self.parameters:
                return False
            elif self.return_type and other.return_type != self.return_type:
                return False
            # lambdas must match
            elif self.is_lambda != other.is_lambda:
                return False
            # async's must match
            elif self.is_async != other.async:
                return False
        # if it is a struct or enum template, types must match
        elif self.template_type in {self.TemplateTypes.STRUCT, self.TemplateTypes.ENUM}:
            for member in self.members:
                if member not in other.members:
                    return False
        # if it is a module check qualifications
        elif self.template_type == self.TemplateTypes.MODULE:
            # check constructor
            if self.constructor:
                if modules.get_constructor(other) != self.constructor:
                    return False
            # check properties
            if self.members:
                if any(x not in other.members for x in self.members):
                    return False
            # check methods
            if self.interface:
                if any(x not in other.members for x in self.interface):
                    return False
        # passed all tests, assume valid
        return True


# generates the template type itself (from 'template' ast)
def generate_template(ast):
    # all first elements are tokens
    # generate type template
    if ast.content[0].type == 'DATA_TYPE':
        # type list is the second element in the AST
        return Template(Template.TemplateTypes.TYPE, type_list=generate_type_list(ast.content[2]))
    # generate function template
    elif ast.content[0].type in {'FUNC', 'ASYNC', 'LAMBDA'}:
        # dictionary of components to synthesized into a template
        template_components = {
            'parameters': None,
            'return_type': None,
            'async': ast.content[0].type == 'ASYNC',
            'lambda': ast.content[0].type == 'LAMBDA'
        }
        # if the template is empty
        if isinstance(ast.content[-2], Token):
            return Template(Template.TemplateTypes.FUNC, **template_components)
        # extract specific elements
        for item in ast.content[-2].content:
            # all items are AST nodes
            if item.name == 'template_params':
                template_components['parameters'] = generate_type_list(item.content[1])
            elif item.name == 'template_return':
                template_components['return_type'] = generate_type_list(item.content[1])
        # return completed function template
        return Template(Template.TemplateTypes.FUNC, **template_components)


def generate_type_list(ast):
    content = ast.content
    type_list = []
    for item in content:
        # only necessary elements are ASTNodes
        if isinstance(item, ASTNode):
            # add generated type if it is a data type
            if item.name == 'types':
                type_list.append(generate_type(item))
            # extend list to incorporate next elements
            elif item.name == 'n_type_template':
                type_list.extend(item.content)
    return type_list


def template_cast(template, dt):
    pass


from syc.icg.generators.data_types import generate_type
