from syc.icg.types import Template, OBJECT_TEMPLATE
from syc.ast.ast import ASTNode, Token


from syc.icg.generators.data_types import generate_type
from syc.icg.generators.structs import generate_members as generate_struct_members
from syc.icg.generators.enum import generate_members as generate_enum_members
from syc.icg.generators.module_body import generate_constructor, generate_member
from syc.icg.generators.blocks import generate_interface_body


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
    # generate struct template
    elif ast.content[0].type == 'STRUCT':
        # check for null struct
        if isinstance(ast.content[2], Token):
            return Template(Template.TemplateTypes.STRUCT, members=[])
        # generate normal struct template
        return Template(Template.TemplateTypes.STRUCT, members=generate_struct_members(ast.content[2]))
    # generate enum template
    elif ast.content[0].type == 'ENUM':
        # check for null enum
        if isinstance(ast.content[2], Token):
            return Template(Template.TemplateTypes.ENUM, members=[])
        # generate normal enum template
        return Template(Template.TemplateTypes.ENUM, members=generate_enum_members(ast.content[2]))
    # generate module template
    else:
        # dictionary of components to synthesized into a module template
        template_module = {
            'members': None,
            'interface': None,
            'constructor': None
        }
        # check for null module
        if isinstance(ast.content[2], Token):
            return Template(Template.TemplateTypes.MODULE, **template_module)
        # generate from components
        for item in ast.content[2].content:
            # all components are ASTNodes
            if item.name == 'template_constructor':
                template_module['constructor'] = generate_constructor(item.content[0])
            elif item.name == 'template_properties':
                template_module['members'] = generate_member(item.content[0])
            elif item.name == 'template_interface':
                template_module['interface'] = generate_interface_body(item.content[0])


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
