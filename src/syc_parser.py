import src.gramtools as gramtools
from util import ASTNode
from util import Token
import src.errormodule as er

# update parsing algorithm


class Parser:
    def __init__(self, input_buffer):
        self.input_buffer = input_buffer
        self.follow_table = {}

    # main parsing method
    @staticmethod
    def run_parser(table, grammar, input_tokens):
        # primes stack and ect.
        # position in input
        pos = 0
        # ast_string = ""
        header = ""
        # stack declaration
        stack = ["$", grammar.start_symbol]
        # stack for holding building AST
        sem_stack = [ASTNode(grammar.start_symbol)]
        input_tokens.append(("", "$"))
        # enter cycle
        while len(stack) > 0:
            print(sem_stack)
            if stack[len(stack) - 1] == "queue":
                # handles closing of ASTs
                # ast_string += ")"
                sem_stack[-2].content.append(sem_stack[-1])
                sem_stack.pop()
                stack.pop()
                continue
            # handles nonterminals
            elif stack[len(stack) - 1] in grammar.nonterminals:
                if header != "":
                    # ast_string += header
                    sem_stack.append(ASTNode(header))
                    header = ""
                # nt = stack.pop() + "("
                nt = stack.pop()
                header = nt
                if table[nt][input_tokens[pos].type] != ["$"]:
                    stack += reversed(table[nt][input_tokens[pos].type] + ["queue"])
            # handles epsilon
            elif stack[-1] == "&":
                stack.pop()
                if stack[-1] == "queue":
                    stack.pop()
                    # ast_string = ast_string[:len(ast_string) - 1]
                    sem_stack.pop()
            # handles terminals
            else:
                if stack[len(stack) - 1] == input_tokens[pos].type:
                    if header != "":
                        # ast_string += header
                        sem_stack.append(ASTNode(header))
                        header = ""
                    if input_tokens[pos] != "$":
                        # ast_string += "[" + input[pos][0] + "," + input[pos][1] + "]"
                        sem_stack[-1].content.append(input_tokens[pos])
                    stack.pop()
                else:
                    er.throw("Unexpected Token", "syntax_error", input_tokens)
                pos += 1
        print("Returning")
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
                first = self.first(grammar=grammar, production=sub_pro)
                # if there is an epsilon, gets follows
                for item in first:
                    if item == "&":
                        follow = self.follow(production, grammar)
                        for f in follow:
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
                    # print(subPro)
                    # finds its location
                    ndx = subPro.index(symbol)
                    # each evaluates a follow patterns as dictated by follow docs
                    # aB
                    if ndx > len(subPro) - 1 and symbol != name:
                        follow = self.follow(name, grammar)
                        for item in follow:
                            add_to_follow_set(item)
                    elif ndx < len(subPro) - 1:
                        next_symbol = subPro[ndx + 1]
                        # terminals
                        if next_symbol in grammar.terminals:
                            add_to_follow_set(next_symbol)
                        # aB&
                        elif next_symbol == "&":
                            follow = self.follow(name, grammar)
                            for item in follow:
                                add_to_follow_set(item)
                        # aBc
                        else:
                            for nt_follow in self.non_terminal_follow(grammar, name, subPro, ndx):
                                add_to_follow_set(nt_follow)
        self.follow_table[symbol] = follow_set
        return follow_set

    def non_terminal_follow(self, grammar, name, sub_pro, ndx):
        nt_follow_set = []
        next_symbol = sub_pro[ndx + 1]

        def add_to_nt_follow_set(char):
            if char not in nt_follow_set:
                nt_follow_set.append(char)

        if next_symbol in grammar.terminals:
            return [next_symbol]
        firsts = self.first(grammar, grammar.productions[next_symbol])
        for first in firsts:
            if first != "&":
                add_to_nt_follow_set(first)
            else:
                if ndx + 2 < len(sub_pro):
                    for nt_follow in self.non_terminal_follow(grammar, name, sub_pro, ndx + 1):
                        add_to_nt_follow_set(nt_follow)
                else:
                    for nt_follow in self.follow(name, grammar):
                        add_to_nt_follow_set(nt_follow)
        return nt_follow_set

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
        # if first item is a terminal, add to first list
        if production[0] in grammar.terminals or production[0] == "&":
            add_to_first_list(production[0])
        # if first item in non-terminal, recur and add the result to first list
        else:
            first = self.first(grammar, grammar.productions[production[0]])
            add_to_first_list(first)
        return first_list

    def parse(self):
        # loads in the grammar
        g = gramtools.build_grammar()
        # generate parsing table
        p_table = self.generate_table(g)


