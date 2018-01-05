import json
import util


def load_package(name):
    index = json.loads(open(util.source_dir + "/lib/package_index.json").read())
    if name in index.keys():
        make_dependency(name, index[name])
        return open(index[name]).read()
    else:
        make_dependency(name.split(".")[0].split("/")[-1], name)
        return open(name).read()


# adds data to a dependency file that will be use later when the compiler is acquiring packages
def make_dependency(name, path):
    with open("_build/dependencies.json", "w+") as file:
        json.dump({name: path}, file)
        file.close()
