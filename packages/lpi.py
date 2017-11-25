import json
import util


package_index = json.loads(open("package_index.json").read())


def package_exists(name):
    return name in package_index.keys()


def open_package(name):
    if package_exists(name):
        return package_index[name]
    else:
        raise(util.CustomException("Package Error: Unable to find package by name '%s'." % name))
