from src.sem_tools import Attribute
from json import loads
from util import source_dir


def get_attributes(item, context):
    attribute_table = loads(open(source_dir + "/src/config/attributes.json").read())
    if context == "node":
        pass
    else:
        pass


def generate_attr_obj(attr_str):
    return Attribute("", attr_str)
