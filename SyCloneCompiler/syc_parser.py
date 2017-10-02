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
            "test3": "test3 => \"OPEN_PAREN\" test3 \"CLOSE_PAREN\" / A / &;A => \"test\"",
            "int_pos_math": "E => T E`;E` => \"PLUS\" T E` / &;T => F T`;T` => \"TIMES\" F T` / &;F => G F`;F` => \"EXPONENT\" G F` / &;G => \"INTEGER_LITERAL\" / \"IDENTIFIER\""
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
                    follows = self.GetFollows(G)
                    p_table = self.GenerateTable(G, follows)
                    end_symbol = item[len(item) - 1]
                    temp_item = item[:len(item) - 1]
                    node = ""
                    try:
                        node = self.EnterCycle(p_table, G, temp_item, end_symbol[0], True)
                    except Exception as e:
                        continue
                    tree += node + "\n"
        #print(tree)
        return tree

    def EnterCycle(self, table, grammar, input, end_symbol, isMain, pos = 0):
        ast_string = ""
        header = ""
        stack = [ "$", grammar.start_symbol ]
        input.append(("", "$"))
        while(len(stack) > 0):
            if(stack[len(stack) - 1] == "queue"):
                ast_string += ")"
                stack.pop()
                continue
            elif(stack[len(stack) - 1] in grammar.nonterminals):
                if(header != ""):
                    ast_string += header
                    header = ""
                nt = stack.pop()
                if (nt == grammar.start_symbol):
                    header = nt + "("
                else:
                    header = "("
                if(table[nt][input[pos][1]] != ["$"]):
                    stack += reversed(table[nt][input[pos][1]] + ["queue"])
            elif(stack[-1] == "&"):
                stack.pop()
                if(stack[-1] == "queue"):
                    stack.pop()
                    ast_string = ast_string[:len(ast_string) - 1]
            else:
                if(stack[len(stack) - 1] == input[pos][1]):
                    if (header != ""):
                        ast_string += header
                        header = ""
                    if(input[pos][1] != "$"):
                        ast_string += "[" + input[pos][0] + "," + input[pos][1] + "]"
                    stack.pop()
                else:
                    if(stack[len(stack) - 1][0] == "*"):
                        G = gramtools.BuildGrammar(self.grammars[stack[len(stack) - 1][1:len(stack[-1])]])
                        follows = self.GetFollows(G)
                        p_table = self.GenerateTable(G, follows)
                        rt = self.EnterCycle(p_table, G, input, "", False, pos)
                        stack = rt[1]
                        ast_string += rt[0]
                        pos = rt[2]
                        pass
                    else:
                       if(isMain):
                           pass
                           # print("Invalid Grammar")
                       else:
                           return ((ast_string, stack, pos))
                pos += 1
        return ast_string.rstrip("(") + ")" + end_symbol

    def GenerateTable(self, grammar, follows):
        parsing_table = {}
        for production in grammar.productions:
            parsing_table[production] = {}
            for subpro in grammar.productions[production]:
                first = self.First(grammar=grammar, production=[subpro])
                for item in first:
                    if (item == "&"):
                        follow = follows[production]
                        for f in follow:
                            parsing_table[production][f] = subpro
                    else:
                        parsing_table[production][item] = subpro
        return parsing_table




    #broken
    """def GetProduction(self, grammar, non_terminal, terminal, isFirst):
        production = grammar.productions[non_terminal]
        print(production)
        print(terminal)
        for item in production:
            if (isFirst):
                firsts = self.First(grammar, [item])
                print(firsts)
                if (terminal in firsts):
                    return item
            else:
                follows = self.GetFollow(non_terminal, grammar)
                print(follows)
                if (terminal in follows):
                    return item"""

    """def GetSets(self, grammar):
        firstSet = {}
        for item in grammar.productions:
            firstSet[item] = self.First(grammar, grammar.productions[item])
        followSet = self.Follow(grammar)
        return ((firstSet, followSet))"""

    def GetFollows(self, grammar):
        followTable = {}
        def AddToFollowTable(name, symbol):
            if (item in followTable.keys()):
                followTable[item] += symbol
            else:
                followTable[item] = symbol
        for item in grammar.productions:
            AddToFollowTable(item, self.Follow(item, grammar))
        return followTable

    def First(self, grammar, production):
        firstList = []
        def AddToFirstList(obj):
            if(isinstance(obj, list)):
                for item in obj:
                    if(item not in firstList):
                        firstList.append(item)
            else:
                if(obj not in firstList):
                    firstList.append(obj)
        for item in production:
            if(item[0] in grammar.terminals or item[0] == "&"):
                AddToFirstList(item[0])
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
                AddToFirstList(first)
        return firstList

    def Follow(self, symbol, grammar):
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
        #print(followSet)
        return followSet