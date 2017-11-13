import json
import util


# open a SyClone package
def open_package(name):
    # open the package index
    json_obj = json.loads(open(util.source_dir + "/packages/package_index.json").read())
    # if package is in ndx, open it from the directory specified there.
    if name in json_obj.keys():
        f_content = ""
        with open(util.source_dir + json_obj[name]) as fileObj:
            for item in fileObj:
                f_content += item
        # make a dependency
        make_dependency(name, json_obj[name])
        return f_content
    # try to open it from the current working dir
    try:
        # if this fails => file doesn't exist
        f_content = ""
        with open(name + ".sy") as fileObj:
            for item in fileObj:
                f_content += item
        make_dependency(name, name + ".sy")
        return f_content
    except:
        raise(util.CustomException("Package Error: Unable to locate the package \"%s\"."))


# adds data to a dependency file that will be use later when the compiler is acquiring packages
def make_dependency(name, path):
    with open("_build/dependencies.json", "w+") as file:
        json.dump({name: path}, file)
        file.close()
