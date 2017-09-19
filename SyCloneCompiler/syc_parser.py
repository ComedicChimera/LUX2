import gramtools

class Parser:
    def __init__(self):
        self.main_tree = []
        self.grammars = {
            "test": "S => B \"b\" / C \"d\";B => \"a\" B / &;\"c\" C / &"
        }

    #splits the tokens in statement groups
    def Buffer(self, tokens):
        splitTokens = []
        tokenGroup = []
        for token in tokens:
            if(token == (";","SEMICOLON") or token == ("}", "CLOSE_CURLY") or token == ("{", "OPEN_CURLY")):
                tokenGroup.append(token)
                splitTokens.append(tokenGroup)
                tokenGroup = []
            else:
                tokenGroup.append(token)
        return splitTokens

    def Parse(self, tokens):
        for grammar in self.grammars:
            G = gramtools.BuildGrammar(self.grammars[grammar])
            print("Sets:")
            sets = self.GetSets(G)
            print(sets)
            p_table = self.GenerateTable(G, sets)
            print(p_table)


    def GenerateTable(self, grammar, sets):
        parsing_table = {}
        for n_t in grammar.nonterminals:
            parsing_table[n_t] = {}
            for t in grammar.terminals:
                #place in appropriate first and follow
                parsing_table[n_t][t] = []
        return parsing_table

    def GetSets(self, grammar):
        firstSet = {}
        for item in grammar.productions:
            firstSet[item] = self.First(grammar, grammar.productions[item])
        followSet = self.Follow(grammar)
        return ((firstSet, followSet))

    def First(self, grammar, production):
        firstList = []
        for item in production:
            if(item[0] in grammar.terminals):
                firstList.append(item[0])
            elif(item[0] == "&"):
                firstList.append("&")
            else:
                first = self.First(grammar, grammar.productions[item[0]])
                counter = 1
                while("&" in first):
                    first.remove("&")
                    if(item[counter] in grammar.nonterminals):
                        first += self.First(grammar, grammar.productions[item[counter]])
                    else:
                        first.append(item[counter])
                    counter += 1
                firstList += first
        return firstList

    def Follow(self, grammar):
        followTable = {}
        def AddToFollowTable(name, symbol):
            if (item in followTable.keys()):
                followTable[item] += symbol
            else:
                followTable[item] = symbol
        for item in grammar.productions:
            AddToFollowTable(item, self.GetFollow(item, grammar))
        return followTable


    def GetFollow(self, symbol, grammar):
        followSet = []
        def AddToFollowSet(char):
            if(char not in followSet):
                followSet.append(char)
        if(symbol == grammar.start_symbol):
            AddToFollowSet("$")
        for name in grammar.productions:
            production = grammar.productions[name]
            for subPro in production:
                if(symbol in subPro and symbol != name):
                    ndx = subPro.index(symbol)
                    if (ndx >= len(subPro) - 1):
                        follow = self.GetFollow(name, grammar)
                        for item in follow:
                            AddToFollowSet(item)
                    else:
                        nextSymbol = subPro[ndx + 1]
                        if(nextSymbol in grammar.terminals):
                            AddToFollowSet(nextSymbol)
                        elif(nextSymbol == "&"):
                            follow = self.GetFollow(name, grammar)
                            for item in follow:
                                AddToFollowSet(item)
                        else:
                            follow = self.First(grammar, grammar.productions[nextSymbol])
                            for item in follow:
                                if (item != "&"):
                                    AddToFollowSet(item)
                                else:
                                    follow2 = self.GetFollow(name, grammar)
                                    for item in follow2:
                                        AddToFollowSet(item)
                                    break
        return followSet