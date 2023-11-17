from os import path, makedirs
from .utils import relative_path


def create_directory_if_not_exists(passed_path):
    dir_path =  relative_path(passed_path, 0)
    if not path.exists(dir_path):
        makedirs(dir_path)


def create_cache_directory_if_not_exists():
    create_directory_if_not_exists('cache/')

def create_directories_if_not_exists():
    create_directory_if_not_exists('tasks/')
    create_directory_if_not_exists('output/')
    create_directory_if_not_exists('profiles/')