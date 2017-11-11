import src.gramtools as gramtools
import src.errormodule as er
import src.ASTtools as ASTtools


class Parser:
    def __init__(self):
        pass

    def parse(self, tokens):
        # gets grammar for gramtools
        g = gramtools.build_grammar()
        # gets a set of follows to be used later
        follows = self.get_follows(g)
        # generates parsing table
        p_table = self.generate_table(g, follows)
        # calls main parsing algorithm
        node = self.run_parser(p_table, g, tokens)
        print(node)
        return node

    @staticmethod
    def run_parser(table, grammar, input_tokens):
        # primes stack and ect.
        # position in input
        pos = 0
        # real position in string for error handling
        rt_pos = 0
        # ast_string = ""
        header = ""
        # stack declaration
        stack = ["$", grammar.start_symbol ]
        # stack for holding building AST
        sem_stack = [ASTtools.ASTNode(grammar.start_symbol)]
        input_tokens.append(("", "$"))
        # enter cycle
        while len(stack) > 0:
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
                    sem_stack.append(ASTtools.ASTNode(header))
                    header = ""
                # nt = stack.pop() + "("
                nt = stack.pop()
                header = nt
                if table[nt][input_tokens[pos][1]] != ["$"]:
                    stack += reversed(table[nt][input_tokens[pos][1]] + ["queue"])
            # handles epsilon
            elif stack[-1] == "&":
                stack.pop()
                if stack[-1] == "queue":
                    stack.pop()
                    # ast_string = ast_string[:len(ast_string) - 1]
                    sem_stack.pop()
            # handles terminals
            else:
                rt_pos += len(input_tokens[pos][1])
                if stack[len(stack) - 1] == input_tokens[pos][1]:
                    if header != "":
                        # ast_string += header
                        sem_stack.append(ASTtools.ASTNode(header))
                        header = ""
                    if input_tokens[pos][1] != "$":
                        # ast_string += "[" + input[pos][0] + "," + input[pos][1] + "]"
                        sem_stack[-1].content.append(ASTtools.Token(input_tokens[pos][0], input_tokens[pos][1]))
                    stack.pop()
                else:
                    er.throw("Unexpected Token", "syntax_error", [rt_pos, len(input_tokens[pos][0])])
                pos += 1
        print(sem_stack)
        # return ast_string.rstrip("(") + ")" + end_symbol
        return sem_stack[0]

    # generates the parsing table
    def generate_table(self, grammar, follows):
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
                        follow = follows[production]
                        for f in follow:
                            parsing_table[production][f] = sub_pro
                    else:
                        parsing_table[production][item] = sub_pro
        return parsing_table

    def get_follows(self, grammar):
        # primes follow table
        follow_table = {}

        # interior func to add items to follow table
        def add_to_follow_table(symbol):
            if item in follow_table.keys():
                follow_table[item] += symbol
            else:
                follow_table[item] = symbol
        # iterates through productions getting follows
        for item in grammar.productions:
            print("\n" * 3)
            add_to_follow_table(self.follow(item, grammar))
        return follow_table

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
        # iterates through sub-pros
        for item in production:
            # if first item is a terminal, add to first list
            if item[0] in grammar.terminals or item[0] == "&":
                add_to_first_list(item[0])
            # if first item in non-terminal, recur and add the result to first list
            else:
                print(item[0])
                first = self.first(grammar, grammar.productions[item[0]])
                # possibly unnecessary
                """counter = 1
                while("&" in first):
                    first.remove("&")
                    if(item[counter] in grammar.nonterminals):
                        first += self.First(grammar, grammar.productions[item[counter]])
                    else:
                        first.append(item[counter])
                    counter += 1"""
                add_to_first_list(first)
        return first_list

    def follow(self, symbol, grammar):
        # sets up follow set
        follow_set = []

        print(symbol)

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
                    # each evaluates a follow patterns as dictated by follow docs
                    if ndx >= len(subPro) - 1 and symbol != name:
                        follow = self.follow(name, grammar)
                        for item in follow:
                            add_to_follow_set(item)
                    elif ndx + 1 < len(subPro):
                        next_symbol = subPro[ndx + 1]
                        if next_symbol in grammar.terminals:
                            add_to_follow_set(next_symbol)
                        elif next_symbol == "&":
                            follow = self.follow(name, grammar)
                            for item in follow:
                                add_to_follow_set(item)
                        else:
                            print(next_symbol)
                            follow = self.first(grammar, grammar.productions[next_symbol])
                            for item in follow:
                                if item != "&":
                                    add_to_follow_set(item)
                                else:
                                    follow2 = self.follow(name, grammar)
                                    for item in follow2:
                                        add_to_follow_set(item)
        return follow_set
