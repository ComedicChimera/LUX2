import re
from util import SyCloneRecoverableError
from syc.ast.ast import ASTNode, unparse

code = ""


def get_position(ndx):
    new_lines = list(re.finditer("\n", code))
    if len(new_lines) == 0:
        return [0, ndx]
    line = 0
    for num in range(len(new_lines)):
        if ndx <= new_lines[num].start():
            if num > 0:
                ndx -= new_lines[num - 1].start() + 1
                break
            else:
                break
        line += 1
    else:
        ndx -= new_lines[-1].start() + 1
    return line, ndx


def getln(line, ndx, len_carrots):
    return code.split("\n")[line] + "\n" + " " * ndx + ("^" * len_carrots)


def throw(error_type, error, params):
    if error_type == 'semantic_error':
        _print_semantic_error(error, params)
    elif error_type == 'syntax_error':
        _print_syntax_error(error, params)


def warn(message, params):
    if isinstance(params, ASTNode):
        raw_tokens = unparse(params)
    else:
        raw_tokens = [params]
    line, ndx = get_position(raw_tokens[0].ndx)
    print('[WARNING] %s %s' % (message, '[line:%d position:%d]' % (line, ndx)))


def _print_semantic_error(message, params):
    if isinstance(params, ASTNode):
        raw_tokens = unparse(params)
    else:
        raw_tokens = [params]
    len_carrots = (raw_tokens[-1].ndx + len(raw_tokens[-1].value)) - raw_tokens[0].ndx if len(raw_tokens) > 1 else len(raw_tokens[0].value)
    line, ndx = get_position(raw_tokens[0].ndx)
    message += ' [line:%d position:%d]' % (line, ndx)
    message += '\n\n%s' % getln(line, ndx, len_carrots)
    raise SyCloneRecoverableError(message)


def _print_syntax_error(message, params):
    len_carrots = len(params[0].value)
    line, ndx = get_position(params[0].ndx)
    message += ' [line:%d position:%d]' % (line, ndx)
    message += '\n\n%s' % getln(line, ndx, len_carrots)
    message += '\n\nExpected: ' + (', '.join(map(token_transform, params[1])) if isinstance(params[1], list) else token_transform(params[1]))
    print(message)
    exit(1)


def token_transform(token):
    remaps = {
        'AMP': '&'
    }
    if token in remaps:
        return remaps[token]
    elif len(token) == 1:
        return token
    return ''.join(map(lambda t: t[0] + t[1:].lower(), token.split('_')))
