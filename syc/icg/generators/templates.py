from syc.icg.types import Template, OBJECT_TEMPLATE
from syc.ast.ast import Token, ASTNode
from syc.icg.generators.data_types import generate_type
import syc.icg.modules as modules


# generates the template type itself (from 'template' ast)
def generate_template(ast):
    # all first elements are tokens
    # generate type template
    if ast.content[0].type == 'DATA_TYPE':
        # check for null type template
        if isinstance(ast.content[2], Token):
            return OBJECT_TEMPLATE
        # type list is the second element in the AST
        return Template(Template.TemplateTypes.TYPE, type_list=generate_type_list(ast.content[2]))
    # generate function template
    elif ast.content[0].type in {'FUNC', 'ASYNC'}:
        # dictionary of components to synthesized into a template
        template_components = {
            'parameters': None,
            'return_type': None,
            'async': ast.content[0].type == 'ASYNC',
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
    # generate module template
    else:
        # check for empty modules
        if isinstance(ast.content[-2], Token):
            return Template(Template.TemplateTypes.MODULE, members=[])
        # generate normal module template
        return Template(Template.TemplateTypes.MODULE, members=modules.generate_body(ast.content[-2]))


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
