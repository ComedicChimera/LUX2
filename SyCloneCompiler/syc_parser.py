import gramtools
import errormodule as er

class Parser:
    def __init__(self):
        pass

    def Parse(self, tokens):
        G = gramtools.BuildGrammar()
        follows = self.GetFollows(G)
        p_table = self.GenerateTable(G, follows)
        node = self.EnterCycle(p_table, G, tokens, ";", True)
        return node

    def EnterCycle(self, table, grammar, input, end_symbol, isMain, pos = 0):
        rt_pos = 0
        ast_string = ""
        header = ""
        stack = [ "$", grammar.start_symbol ]
        input.append(("", "$"))
        while(len(stack) > 0):
            if(stack[len(stack) - 1] == "queue"):
                ast_string += ")\t"
                stack.pop()
                continue
            elif(stack[len(stack) - 1] in grammar.nonterminals):
                if(header != ""):
                    ast_string += header
                    header = ""
                nt = stack.pop()
                header = nt + "("
                if(table[nt][input[pos][1]] != ["$"]):
                    stack += reversed(table[nt][input[pos][1]] + ["queue"])
            elif(stack[-1] == "&"):
                stack.pop()
                if(stack[-1] == "queue"):
                    stack.pop()
                    ast_string = ast_string[:len(ast_string) - 1]
            else:
                if(stack[-1] == "OPEN_CURLY" and input[pos][1] == "OPEN_CURLY" and stack[-2] == "$"):
                    ast_string += "{\n"
                    ast_string = self.Parse(input[pos:len(input)])
                rt_pos += len(input[pos][1])
                if(stack[len(stack) - 1] == input[pos][1]):
                    if (header != ""):
                        ast_string += header
                        header = ""
                    if(input[pos][1] != "$"):
                        ast_string += "[" + input[pos][0] + "," + input[pos][1] + "]\t"
                    stack.pop()
                else:
                    er.Throw("Unexpected Token", "syntax_error", [rt_pos, len(input[pos][0])])
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
        return followSet