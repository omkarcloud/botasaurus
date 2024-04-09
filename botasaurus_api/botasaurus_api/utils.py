import json
from os import path, makedirs, getcwd

def relative_path(target_path, goback=0):
    levels = [".."] * (goback + -1)
    return path.abspath(path.join(getcwd(), *levels, target_path.strip()))

def create_directory_if_not_exists(passed_path):
    dir_path = relative_path(passed_path, 0)
    if not path.exists(dir_path):
        makedirs(dir_path)


def create_output_directory_if_not_exists():
    create_directory_if_not_exists("output")
    create_directory_if_not_exists("output/responses")

output_directory_created = False
 
def write_json_response(path, data,  indent=4):
    global output_directory_created
    # Check if output directory exists, if not, create it
    if not output_directory_created:
        create_output_directory_if_not_exists()
        output_directory_created = True

    with open("output/responses/" + path + ".json", 'w', encoding="utf-8") as fp:
        json.dump(data, fp, indent=indent)

