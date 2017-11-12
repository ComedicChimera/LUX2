import json
import util


def open_package(name):
    json_obj = json.loads(open(util.source_dir + "/packages/package_index.json").read())
    if name in json_obj.keys():
        f_content = ""
        with open(json_obj[name]) as fileObj:
            for item in fileObj:
                f_content += item
        make_dependency(name, json_obj[name])
        return f_content
    try:
        f_content = ""
        with open(name + ".sy") as fileObj:
            for item in fileObj:
                f_content += item
        make_dependency(name, name + ".sy")
        return f_content
    except:
        raise(util.CustomException("Package Error: Unable to locate the package \"%s\"."))


def make_dependency(name, path):
    with open("_build/dependencies.json", "w+") as file:
        json.dump({name: path}, file)
        file.close()
