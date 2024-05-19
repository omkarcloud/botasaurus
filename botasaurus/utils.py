import json
import os

def is_errors_instance(instances, error):
    for i in range(len(instances)):
        ins = instances[i]
        if isinstance(error, ins):
            return True, i
    return False, -1

def relative_path(path, goback=0):
    levels = [".."] * (goback + -1)
    return os.path.abspath(os.path.join(os.getcwd(), *levels, path.strip()))

def remove_nones(list):
    return [element for element in list if element is not None]

def write_html( data, path,):
    with open(path, 'w', encoding="utf-8") as fp:
        fp.write(data)


def write_file( data, path,):
    with open(path, 'w', encoding="utf-8") as fp:
        fp.write(data)


def read_json(path):
    with open(path, 'r', encoding="utf-8") as fp:
        data = json.load(fp)
        return data

def read_file(path):
    with open(path, 'r', encoding="utf-8") as fp:
        content = fp.read()
        return content
        
def write_json(data, path,  indent=4):
    with open(path, 'w', encoding="utf-8") as fp:
        json.dump(data, fp, indent=indent)



def uniquify_strings(strs):
    return list(dict.fromkeys(strs))
