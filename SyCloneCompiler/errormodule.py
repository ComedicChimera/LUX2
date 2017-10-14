import re

code = ""
bG = [0, ""]

#buggy
def Throw(type, error, params):
    if(type == "lexerror"):
        tempCode = code
        ndx = tempCode.index(params)
        tCode = code.replace("\t", "").split("\n")
        count = 0
        lncount = 0
        for item in tCode:
            count += len(item)
            if(count > ndx + len(params)):
                lncount -= 1
                break
            lncount += 1
        print("\n" + bcolors.RED + error + " (\'" + params + "\') [ln:" + str(lncount) + " - " + str(tCode[lncount].index(params) + 1) + "]:")
        print(tCode[lncount])
        print(" " * tCode[lncount].index(params) + "^" * len(params))
    elif(type == "syntax_error"):
        #try:
            d = ";"
            sCode = [e.replace("\n","")+d for e in code.split(d) if e]
            stmt = sCode[params]
            print(stmt)
            print(sCode)
            print(bG[1])
            rx = re.compile(re.escape(bG[1]))
            possibleTokens = rx.findall(stmt)
            print(possibleTokens)
            for item in possibleTokens:
                if (stmt.index(item) > bG[0]):
                    i = 0
                    for istmt in code.split("\n"):
                        if (stmt in istmt):
                            print("\n" + bcolors.RED + error + " (\'" + bG[1] + "\') [ln:" + str(i) + " - " + str(stmt.index(item)) + "]:")
                            print(stmt)
                            print(" " * stmt.index(item) + "^" * len(bG[1]))
                            break
                        i += 1
                    break
                else:
                    stmt = stmt.replace(bG[1], "~" * len(bG[1]))
        #except Exception as e:
            #print("Exception generated")
            #print(bcolors.RED + str(e))
    elif(type == "end_symbol_error"):
        print(bcolors.RED + "Invalid end of statement.")

    exit(0)

"""def Log(action, level, end="\n"):
    global log_level
    if (level >= log_level):
        if (level > 2):
            Throw(action)
        else:
            print(action, end=end)"""

class CustomException(Exception):
    pass

class bcolors:
    MAGENTA = '\033[35m'
    BLUE = '\033[34m'
    GREEN = '\033[32m'
    YELLOW = '\033[93m'
    RED = '\033[31m'
    WHITE = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'