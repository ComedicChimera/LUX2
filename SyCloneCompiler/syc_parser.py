import gramtools
import errormodule as er

class Parser:
    def __init__(self):
        self.main_tree = []
        self.grammars = {
            #"test": "S => B \"b\" / C \"d\";B => \"a\" B / &;\"c\" C / &",
            #"test2": "S => \"(\" A \")\";A => \"a\" A / &",
            #"test4": "E => T E';E' => \"+\" T E' / &;T => F T';T' => \"*\" F T' / &;F => \"(\" E \")\" / \"id\"",
            #"test5": "S => \"(\" A \")\";A => \"a\" A",
            "test3": "test3 => \"OPEN_PAREN\" test3 \"CLOSE_PAREN\" / &"
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
        else:
            splitTokens.append(tokenGroup)
        return splitTokens

    def Parse(self, tokens):
        tree = ""
        for item in tokens:
            if(item != []):
                for grammar in self.grammars:
                    G = gramtools.BuildGrammar(self.grammars[grammar])
                    sets = self.GetSets(G)
                    p_table = self.GenerateTable(G, sets)
                    end_symbol = item[len(item) - 1]
                    temp_item = item[:len(item) - 1]
                    node = ""
                    try:
                        node = self.EnterCycle(p_table, G, temp_item, end_symbol[0], True)
                    except:
                        continue
                    tree += node
        return tree

    def EnterCycle(self, table, grammar, input, end_symbol, isMain, pos = 0):
        action_symbols = []
        ast_string = ""
        header = ""
        stack = [ "$", grammar.start_symbol ]
        input.append(("", "$"))
        while(len(stack) > 0):
            if(stack[len(stack) - 1] in grammar.nonterminals):
                if(header != ""):
                    ast_string += header
                    header = ""
                nt = stack.pop()
                if (nt == grammar.start_symbol):
                    header = nt + "("
                else:
                    header = "("
                a_prod = grammar.productions[nt]
                symbols = []
                for item in a_prod:
                    symbols.append(item[-1])
                action_symbols.append(symbols)
                stack += reversed(table[nt][input[pos][1]])
            elif(stack[len(stack) - 1] == "&"):
                header = ""
                if("&" in action_symbols[0]):
                    action_symbols = action_symbols[1:len(action_symbols)]
                stack.pop()
            else:
                if(stack[len(stack) - 1] == input[pos][1]):
                    if (header != ""):
                        ast_string += header
                        header = ""
                    if(input[pos][1] != "$"):
                        ast_string += "[" + input[pos][0] + "," + input[pos][1] + "]"
                        if (input[pos][1] in action_symbols[0]):
                            ast_string += ")"
                            action_symbols = action_symbols[1:len(action_symbols)]
                    stack.pop()
                else:
                    if(stack[len(stack) - 1][0] == "*"):
                        G = gramtools.BuildGrammar(self.grammars[stack[len(stack) - 1][1:len(stack[-1])]])
                        sets = self.GetSets(G)
                        p_table = self.GenerateTable(G, sets)
                        rt = self.EnterCycle(p_table, G, input, "", False, pos)
                        stack = rt[1]
                        ast_string += rt[0]
                        pos = rt[2]
                        pass
                    else:
                       if(isMain):
                           er.Log("Invalid Grammar", 3)
                       else:
                           return ((ast_string, stack, pos))
                pos += 1
        return ast_string + end_symbol

    def GenerateTable(self, grammar, sets):
        parsing_table = {}
        for n_t in grammar.nonterminals:
            parsing_table[n_t] = {}
            for t in grammar.terminals:
                #place in appropriate first and follow
                parsing_table[n_t][t] = []
            parsing_table[n_t]["$"] = []
        firsts = sets[0]
        follows = sets[1]
        for non_terminal in firsts:
            for terminal in firsts[non_terminal]:
                if(terminal != "&"):
                    parsing_table[non_terminal][terminal] = self.GetProduction(grammar, non_terminal, terminal)
                else:
                    for ft in follows[non_terminal]:
                        parsing_table[non_terminal][ft] = self.GetProduction(grammar, non_terminal, "&")

        return parsing_table

    def GetProduction(self, grammar, non_terminal, terminal):
        production = grammar.productions[non_terminal]
        for item in production:
            if(terminal in item):
                return item

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
                if (symbol in subPro):
                    ndx = subPro.index(symbol)
                    if (ndx >= len(subPro) - 1 and symbol != name):
                        follow = self.GetFollow(name, grammar)
                        for item in follow:
                            AddToFollowSet(item)
                    elif(ndx + 1 < len(subPro)):
                        nextSymbol = subPro[ndx + 1]
                        if (nextSymbol in grammar.terminals):
                            AddToFollowSet(nextSymbol)
                        elif (nextSymbol == "&"):
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

        return followSet