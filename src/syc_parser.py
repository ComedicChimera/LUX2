import src.gramtools as gramtools
import src.errormodule as er
import src.ASTtools as ASTtools


class Parser:
    def __init__(self, ip_buffer):
        self.input_buffer = self.convert_tokens(ip_buffer) + ["$"]
        self.grammar = gramtools.build_grammar()
        self.semantic_stack = []
        self.gen = self.get_next()
        self.look_ahead = self.get_char()

    # next char generator
    def get_next(self):
        pos = 0
        while pos < len(self.input_buffer):
            yield self.input_buffer[pos]
            pos += 1

    # gets the next character in the input buffer
    def get_char(self):
        return next(self.gen)

    # expands a non terminal
    def expand(self, non_terminal):
        return self.grammar.productions[non_terminal]

    # takes in a non terminals productions and determines if the input buffer matches them
    def evaluate(self, productions):
        print(productions)
        print(self.look_ahead)
        pos = 0
        while len(productions) > 0:
            for production in productions:
                if pos >= len(production):
                    if len(productions) == 1:
                        self.look_ahead = self.get_char()
                        return True
                    else:
                        productions.remove(production)
                if not self.match(production, pos):
                    productions.remove(production)
                else:
                    self.look_ahead = self.get_char()
            pos += 1
        return False

    # match takes in token, production, and ndx and returns whether or not the token should be accepted
    def match(self, production, ndx):
        # if the current item is a non terminal, expand and evaluate
        if production[ndx] in self.grammar.nonterminals:
            return self.evaluate(self.expand(production[ndx]))
        # if the current item is &, return true and assume that mismatched indices will be caught later
        elif production[ndx] == "&":
            return True
        # if the current item is a terminal, check if terminal and token type are equal
        elif self.look_ahead.type == production[ndx]:
            return True
        else:
            print(production[ndx])
            return False

    # the main parsing function
    def parse(self):
        if self.evaluate(self.grammar.productions[self.grammar.start_symbol]) and self.look_ahead == "$":
            return self.semantic_stack[0]
        else:
            er.throw("syntax_error", "Unexpected Token", self.look_ahead)

    @staticmethod
    def convert_tokens(buffer):
        new_buffer = []
        for token in buffer:
            new_buffer.append(ASTtools.Token(token[1], token[0]))
        return new_buffer
