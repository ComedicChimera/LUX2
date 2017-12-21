from src.parser.ASTtools import ASTNode
from src.parser.ASTtools import Token

import src.errormodule as er
import src.parser.gramtools as gramtools


# update parsing algorithm


class Parser:
    def __init__(self, input_buffer):
        self.input_buffer = input_buffer
        self.follow_table = {}

    # main parsing method
    def run_parser(self, table, grammar):
        # primes stack and ect.
        # position in input
        pos = 0
        # stack declaration
        stack = ["$", grammar.start_symbol]
        # stack for holding building AST
        sem_stack = [ASTNode(grammar.start_symbol)]
        self.input_buffer.append(Token("$", "$", self.input_buffer[-1].ndx))
        # enter cycle
        while len(stack) > 0:
            if stack[len(stack) - 1] == "queue":
                # handles closing of ASTs
                sem_stack[-2].content.append(sem_stack[-1])
                sem_stack.pop()
                stack.pop()
                continue
            # handles non terminals
            elif stack[len(stack) - 1] in grammar.nonterminals:
                nt = stack.pop()
                sem_stack.append(ASTNode(nt))
                if self.input_buffer[pos].type not in table[nt]:
                    er.throw("syntax_error", "Unexpected Token", [self.input_buffer[pos], [str(x) for x in table[nt].keys()]])
                if table[nt][self.input_buffer[pos].type] != ["$"]:
                    stack += reversed(table[nt][self.input_buffer[pos].type] + ["queue"])
            # handles epsilon
            elif stack[-1] == "&":
                stack.pop()
                if stack[-1] == "queue":
                    stack.pop()
                    sem_stack.pop()
            # handles terminals
            else:
                if stack[len(stack) - 1] == self.input_buffer[pos].type:
                    if self.input_buffer[pos].type != "$":
                        sem_stack[-1].content.append(self.input_buffer[pos])
                    stack.pop()
                else:
                    er.throw("syntax_error", "Unexpected Token", [self.input_buffer[pos], stack[-1]])
                pos += 1
        return sem_stack[0]

    # generates the parsing table
    def generate_table(self, grammar):
        # primes p table
        parsing_table = {}
        # iterates through productions getting firsts and follows and assembling parsing table
        for production in grammar.productions:
            # adds a new entry for the nt productions
            parsing_table[production] = {}
            # checks through each sub-production for the main production
            for sub_pro in grammar.productions[production]:
                # gets first
                first = self.first(grammar=grammar, production=[sub_pro])
                # if there is an epsilon, gets follows
                for item in first:
                    if item == "&":
                        follow = self.follow(production, grammar)
                        for f in follow:
                            if f in parsing_table[production]:
                                print(f)
                                print(production)
                            parsing_table[production][f] = sub_pro
                    else:
                        parsing_table[production][item] = sub_pro
        return parsing_table

    # follow function
    def follow(self, symbol, grammar):

        if symbol in self.follow_table.keys():
            return self.follow_table[symbol]
        # sets up follow set
        follow_set = []

        # avoids repeat chars
        def add_to_follow_set(char):
            if char not in follow_set:
                follow_set.append(char)

        # adds $ for start symbol
        if symbol == grammar.start_symbol:
            add_to_follow_set("$")
        # iterates through each production and then each sub-production
        for name in grammar.productions:
            production = grammar.productions[name]
            for subPro in production:
                # checks if the given symbol is the sub-productions
                if symbol in subPro:
                    # finds its location
                    ndx = subPro.index(symbol)
                    # each evaluates a follow pattern
                    if ndx >= len(subPro) - 1 and symbol != name:
                        follow = self.follow(name, grammar)
                        for item in follow:
                            add_to_follow_set(item)
                    elif ndx < len(subPro) - 1:
                        follows = self.evaluate_follow(grammar, subPro, ndx, name, symbol)
                        for item in follows:
                            add_to_follow_set(item)
        self.follow_table[symbol] = follow_set
        return follow_set

    # evaluate standard follow
    def evaluate_follow(self, grammar, subPro, ndx, name, symbol):
        # sets up follow set
        follow_set = []

        # avoids repeat chars
        def add_to_follow_set(char):
            if char not in follow_set:
                follow_set.append(char)

        follows = self.first(grammar, [subPro[ndx + 1:]])
        for follow in follows:
            if follow != "&":
                add_to_follow_set(follow)
            else:
                if ndx + 2 < len(subPro) - 1:
                    follows2 = self.evaluate_follow(grammar, subPro[ndx + 2:], ndx, name, symbol)
                    for follow2 in follows2:
                        add_to_follow_set(follow2)
                else:
                    follows3 = self.follow(name, grammar)
                    for follow3 in follows3:
                        add_to_follow_set(follow3)
        return follow_set

    # first function
    def first(self, grammar, production):
        # primes first list
        first_list = []

        # sets up add to first list function to make processing easier
        def add_to_first_list(obj):
            if isinstance(obj, list):
                for item in obj:
                    if item not in first_list:
                        first_list.append(item)
            else:
                if obj not in first_list:
                    first_list.append(obj)
        # iterate through productions
        for sub_pro in production:
            # if first item is a terminal, add to first list
            if sub_pro[0] in grammar.terminals or sub_pro[0] == "&":
                add_to_first_list(sub_pro[0])
            # if first item in non-terminal, recur and add the result to first list
            else:
                add_to_first_list(self.non_terminal_first(grammar, sub_pro, 0))
        return first_list
        
    # handles non_terminals in first
    def non_terminal_first(self, grammar, production, pos):
        firsts = []
        first = self.first(grammar, grammar.productions[production[pos]])
        for item in first:
            if item != "&":
                firsts.append(item)
            else:
                if len(production) - 1 >= pos + 1:
                    if production[pos + 1] in grammar.nonterminals:
                        firsts += self.non_terminal_first(grammar, production, pos + 1)
                    else:
                        firsts.append(production[pos + 1])
                else:
                    firsts.append(item)
        return firsts

    def parse(self):
        # loads in the grammar
        g = gramtools.build_grammar()
        # generate parsing table
        p_table = self.generate_table(g)
        # returns result of parsing function
        return self.run_parser(p_table, g)


