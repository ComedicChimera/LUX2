import re

class Grammar:
    def __init__(self):
        self.terminals = []
        self.nonterminals = []
        self.productions = {}
        self.start_symbol = ""

def BuildGrammar(str_grammar):
    splitG = str_grammar.split(";")
    g = Grammar()
    for production in splitG:
        items = production.split(" ")
        items.append("$")
        currentProduction = []
        hasProName = False
        proName = ""
        subPro = []
        for item in items:
            if(re.match(r'"([^"]*)"', item)):
                g.terminals.append(item.strip("\""))
                subPro.append(item.strip("\""))
            elif(item == "/"):
                currentProduction.append(subPro)
                subPro = []
            elif(item == "$"):
                currentProduction.append(subPro)
            elif(item == "=>"):
                continue
            elif(item == "&"):
                subPro.append("&")
            else:
                if(item not in g.nonterminals):
                    g.nonterminals.append(item)
                if(hasProName):
                    subPro.append(item)
                else:
                    proName = item
                    hasProName = True
                if(g.start_symbol == ""):
                    g.start_symbol = item
        g.productions[proName] = currentProduction
    return(g)