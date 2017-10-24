import gramtools
import errormodule as er
import ASTtools

class Parser:
    def __init__(self):
        pass

    def Parse(self, tokens):
        #gets grammar for gramtools
        G = gramtools.BuildGrammar()
        #gets a set of follows to be used later
        follows = self.GetFollows(G)
        #generates parsing table
        p_table = self.GenerateTable(G, follows)
        #calls main parsing algorithm
        node = self.EnterCycle(p_table, G, tokens, ";")
        print(node)
        return node

    def EnterCycle(self, table, grammar, input, end_symbol):
        #primes stack and ect.
        #position in input
        pos = 0
        #real position in string for error handling
        rt_pos = 0
        ast_string = ""
        header = ""
        #stack declaration
        stack = [ "$", grammar.start_symbol ]
        #stack for holding building AST
        sem_stack = [ ASTtools.ASTNode(grammar.start_symbol) ]
        input.append(("", "$"))
        #enter cycle
        while(len(stack) > 0):
            if(stack[len(stack) - 1] == "queue"):
                #handles closing of ASTs
                #ast_string += ")"
                sem_stack[-2].content.append(sem_stack[-1])
                sem_stack.pop()
                stack.pop()
                continue
            #handles nonterminals
            elif(stack[len(stack) - 1] in grammar.nonterminals):
                if(header != ""):
                    #ast_string += header
                    sem_stack.append(ASTtools.ASTNode(header))
                    header = ""
                #nt = stack.pop() + "("
                nt = stack.pop()
                header = nt
                if(table[nt][input[pos][1]] != ["$"]):
                    stack += reversed(table[nt][input[pos][1]] + ["queue"])
            #handles epsilon
            elif(stack[-1] == "&"):
                stack.pop()
                if(stack[-1] == "queue"):
                    stack.pop()
                    #ast_string = ast_string[:len(ast_string) - 1]
                    sem_stack.pop()
            #handles terminals
            else:
                rt_pos += len(input[pos][1])
                if(stack[len(stack) - 1] == input[pos][1]):
                    if (header != ""):
                        #ast_string += header
                        sem_stack.append(ASTtools.ASTNode(header))
                        header = ""
                    if(input[pos][1] != "$"):
                        #ast_string += "[" + input[pos][0] + "," + input[pos][1] + "]"
                        sem_stack[-1].content.append(ASTtools.Token(input[pos][0], input[pos][1]))
                    stack.pop()
                else:
                    er.Throw("Unexpected Token", "syntax_error", [rt_pos, len(input[pos][0])])
                pos += 1
        print(sem_stack)
        #return ast_string.rstrip("(") + ")" + end_symbol
        return sem_stack[0]

    #generates the parsing table
    def GenerateTable(self, grammar, follows):
        #primes ptable
        parsing_table = {}
        #iterates through productions getting firsts and follows and assembling parsing table
        for production in grammar.productions:
            #adds a new entry for the nt productions
            parsing_table[production] = {}
            #checks through each sub-production for the main production
            for subpro in grammar.productions[production]:
                #gets first
                first = self.First(grammar=grammar, production=[subpro])
                #if there is an epsilon, gets follows
                for item in first:
                    if (item == "&"):
                        follow = follows[production]
                        for f in follow:
                            parsing_table[production][f] = subpro
                    else:
                        parsing_table[production][item] = subpro
        return parsing_table

    def GetFollows(self, grammar):
        #primes follow table
        followTable = {}
        #interior func to add items to follow table
        def AddToFollowTable(name, symbol):
            if (item in followTable.keys()):
                followTable[item] += symbol
            else:
                followTable[item] = symbol
        #iterates through productions getting follows
        for item in grammar.productions:
            AddToFollowTable(item, self.Follow(item, grammar))
        return followTable

    def First(self, grammar, production):
        #primes first list
        firstList = []
        #sets up add to first list function to make processing easier
        def AddToFirstList(obj):
            if(isinstance(obj, list)):
                for item in obj:
                    if(item not in firstList):
                        firstList.append(item)
            else:
                if(obj not in firstList):
                    firstList.append(obj)
        #iterates through sub-pros
        for item in production:
            #if first item is a terminal, add to first list
            if(item[0] in grammar.terminals or item[0] == "&"):
                AddToFirstList(item[0])
            #if first item in non-terminal, recur and add the result to first list
            else:
                first = self.First(grammar, grammar.productions[item[0]])
                #possibly unnecessary
                """counter = 1
                while("&" in first):
                    first.remove("&")
                    if(item[counter] in grammar.nonterminals):
                        first += self.First(grammar, grammar.productions[item[counter]])
                    else:
                        first.append(item[counter])
                    counter += 1"""
                AddToFirstList(first)
        return firstList

    def Follow(self, symbol, grammar):
        #sets up follow set
        followSet = []
        #avoids repeat chars
        def AddToFollowSet(char):
            if(char not in followSet):
                followSet.append(char)
        #adds $ for start symbol
        if(symbol == grammar.start_symbol):
            AddToFollowSet("$")
        #iterates through each production and then each sub-production
        for name in grammar.productions:
            production = grammar.productions[name]
            for subPro in production:
                #checks if the given symbol is the sub-productions
                if (symbol in subPro):
                    #finds its location
                    ndx = subPro.index(symbol)
                    #each evaluates a follow patterns as dictated by follow docs
                    if (ndx >= len(subPro) - 1 and symbol != name):
                        follow = self.Follow(name, grammar)
                        for item in follow:
                            AddToFollowSet(item)
                    elif(ndx + 1 < len(subPro)):
                        nextSymbol = subPro[ndx + 1]
                        if (nextSymbol in grammar.terminals):
                            AddToFollowSet(nextSymbol)
                        elif (nextSymbol == "&"):
                            follow = self.Follow(name, grammar)
                            for item in follow:
                                AddToFollowSet(item)
                        else:
                            follow = self.First(grammar, grammar.productions[nextSymbol])
                            for item in follow:
                                if (item != "&"):
                                    AddToFollowSet(item)
                                else:
                                    follow2 = self.Follow(name, grammar)
                                    for item in follow2:
                                        AddToFollowSet(item)
        return followSet