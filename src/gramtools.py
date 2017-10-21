import json

class Grammar:
    def __init__(self):
        self.terminals = []
        self.nonterminals = []
        self.productions = {}
        self.start_symbol = ""

def BuildGrammar():
    jsonObj = json.loads(open("config/grammars.json").read())
    grammar = Grammar()
    grammar.nonterminals = [x for x in jsonObj]
    grammar.start_symbol = next(iter(grammar.nonterminals))
    for key in jsonObj:
        item = jsonObj[key]
        grammar.productions[key] = [x.split(" ") for x in item]
        terminals = []
        for production in item:
            terminals += [x for x in production.split(" ") if x not in grammar.nonterminals]
        for terminal in terminals:
            if(terminal not in grammar.terminals):
                grammar.terminals.append(terminal)
    return grammar
