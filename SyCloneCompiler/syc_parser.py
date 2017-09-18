import gramtools

class Parser:
    def __init__(self):
        self.main_tree = []
        self.grammars = {
            "test": "S => \"IDENTIFIER\" \"PLUS\" \"IDENTIFIER\" / A;A => \"BOOL_LITERAL\""
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
            sets = self.GetSets(G)
            print(sets)
            p_table = self.GenerateTable(G, sets)


    def GenerateTable(self, grammar, sets):
        pass

    def GetSets(self, grammar):
        firstSet = {}
        followSet = {}
        for item in grammar.productions:
            firstSet[item] = self.First(grammar, grammar.productions[item])
            followSet[item] = self.Follow(grammar, grammar.productions[item])
        return ((firstSet, followSet))

    def First(self, grammar, production):
        firstList = []
        print(production)
        for item in production:
            if(item[0] in grammar.terminals):
                firstList.append(item[0])
            else:
                first = self.First(grammar, grammar.productions[item[0]])
                firstList += first
        return firstList

    def Follow(self, grammar, production):
        pass