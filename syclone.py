import sys
from build import build
import util

# dictionary of all possible commands and their respective functions
# functions take a list of str arguments
commands = {
    'get': '',
    'rm': '',
    'build': build,
    'version': lambda _: print(util.VERSION)
}

# current argument set to be passed to functions
c_args = []
# the current operating command
# to prevent command from called at the beginning '' means null command (do not run)
c_command = ''

# for item in starting arguments not including file path
for item in sys.argv[1:]:
    # if the item is a command
    if item in commands:
        # if not null command
        if c_command != '':
            # try to run the function and print exception is failed
            try:
                # get the current command function and execute with the current arguments
                commands[c_command](c_args)
            except util.SyCloneError as se:
                print(se)
        # update it to the new command provided
        c_command = item
    # else add it to current working arguments
    else:
        c_args.append(item)

# ensure all commands are run
if c_command != '':
    commands[c_command](c_args)
