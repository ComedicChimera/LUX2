import src.errormodule as er
import src.semantics.checker.functions as functions
import src.semantics.checker.identifiers as identifiers
import src.semantics.types as types
from src.parser.ASTtools import ASTNode


# assumes sub-expressions will not be passed in -> evaluated by upper-level expression parser
def parse_atom(atom):
    await, new = False
    trailer = None
    base = None
    lb = False
    for item in atom.content:
        if isinstance(item, ASTNode):
            if item.name == 'await':
                await = True
            elif item.name == 'new':
                new = True
            elif item.name == 'trailer':
                trailer = item
            elif item.name == 'base' or item.name == 'lambda':
                base = item
                if item.name == 'lambda':
                    lb = True
    dt = check_trailer(base, trailer, lb)
    return match_prefix(dt, await, new, atom)


def parse_base(base):
    if isinstance(base.content[0], ASTNode):
        if base.content[0].name == 'string':
            if base.content[0].content[0].type == 'STRING_LITERAL':
                return types.String()
            else:
                return types.Char()
        elif base.content[0].name == 'number':
            if base.content[0].content[0].type == 'FLOAT_LITERAL':
                return types.Float()
            elif base.content[0].content[0].type == 'COMPLEX_LITERAL':
                return types.Complex()
            else:
                tk = base.content[0].content[0]
                if int(tk.value) > 2147483647:
                    return types.Long()
                else:
                    return types.Integer()
        elif base.content[0].name == 'byte_literal':
            tk = base.content[0].content[0]
            if len(tk.value) > 4 and tk.value.startswith('0x'):
                return types.List(types.Byte)
            elif len(tk.value) > 10:
                return types.List(types.Byte)
            else:
                return types.Byte
        elif base.content[0].name == 'inline_function':
            return functions.check_inline(base.content[0])
        elif base.content[0].name == 'dict':
            pass
        elif base.content[0].name == 'list':
            pass
        elif base.content[0].name == 'atom_types':
            bt = base.content[0]
            if isinstance(bt.content[0], ASTNode):
                tp = bt.content[0].content[0].type
                type_map = {
                    'INT_TYPE': types.Integer,
                    'BOOL_TYPE': types.Boolean,
                    'CHAR_TYPE': types.Char,
                    'STRING_TYPE': types.String,
                    'COMPLEX_TYPE': types.Complex,
                    'LONG_TYPE': types.Long,
                    'FLOAT_TYPE': types.Float,
                    'BYTE_TYPE': types.Byte
                }
                return types.CoreType(type_map[tp]())
            else:
                pass
    else:
        if base.content[0].type == 'NULL':
            return types.Null()
        elif base.content[0].type == 'IDENTIFIER':
            return identifiers.find(base.content[0].value)
        elif base.content[0].type == 'VALUE':
            return types.Value()
        elif base.content[0].type == 'BOOL_LITERAL':
            return types.Boolean()
        elif base.content[0].type == 'THIS':
            return types.InstancePointer()


def parse_lambda(lb):
    pass


def check_trailer(base, trailer, is_lambda):
    return trailer


def match_prefix(data_type, awaited, is_memset, atom):
    if not data_type.includes(types.Property.ASYNC) and awaited:
        er.throw('semantic_error', 'Unable to await non-asynchronous element', atom)
    elif is_memset:
        if data_type.includes(types.Property.STRUCTURE):
            data_type.add_property(types.Property.INSTANCE)
            return data_type
        elif isinstance(data_type, types.CoreType):
            return data_type.data_type
        else:
            er.throw('semantic_error', 'Unable to dynamically allocate a non-data type', atom)
    return data_type
