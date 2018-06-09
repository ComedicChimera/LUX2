from syc.icg.types import Template
from syc.ast.ast import ASTNode
from syc.icg.generators.data_types import generate_type


# generates the template type itself (from 'template' ast)
def generate_template(ast):
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
    return Template(type_list)