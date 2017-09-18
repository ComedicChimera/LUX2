log_level = 3

def Throw(error):
    print(error)
    exit(0)

def Log(action, level, end="\n"):
    global log_level
    if (level >= log_level):
        if (level > 2):
            Throw(action)
        else:
            print(action, end=end)

class CustomException(Exception):
    pass