from os import path, makedirs
import os

def relative_path(path, goback=0):
    levels = [".."] * (goback + -1)
    return os.path.abspath(os.path.join(os.getcwd(), *levels, path.strip()))

def create_directory_if_not_exists(passed_path):
    dir_path =  relative_path(passed_path)
    if not path.exists(dir_path):
        makedirs(dir_path)

def create_cache_directory_if_not_exists():
    create_directory_if_not_exists('cache/')

output_check_done = False
def create_output_directory_if_not_exists():
    global output_check_done
    if not output_check_done:
        output_check_done = True
        create_directory_if_not_exists('output/')