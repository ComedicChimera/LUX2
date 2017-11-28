"""from lark import Lark
import src.errormodule as er


def parse(input_str):
    grammar = open("config/syc_grammar.ebnf").read()
    parser = Lark(grammar, lexer='standard', parser='lalr')
    try:
        return parser.parse(input_str)
    except Exception as e:
        er.throw("syntax_error", e)"""
