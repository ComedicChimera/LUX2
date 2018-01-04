import json
import lpi


# open a SyClone package
def include(name, is_absolute_path):
    # tests to see if it is able to a package from the package index
    try:
        return lpi.open_package(name)
    except Exception as e:
        # if it can't it will try to open the path according to the users directive and if that fails it will return the default package error
        try:
            if is_absolute_path:
                return open(name).read()
            else:
                return open(name + ".sy").read()
        except:
            raise e


# adds data to a dependency file that will be use later when the compiler is acquiring packages
def make_dependency(name, path):
    with open("_build/dependencies.json", "w+") as file:
        json.dump({name: path}, file)
        file.close()
