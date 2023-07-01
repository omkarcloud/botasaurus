from datetime import datetime
import errno
import json
import sys
from time import sleep
import traceback
from urllib.error import ContentTooShortError
from http.client import RemoteDisconnected
from urllib.error import ContentTooShortError, URLError
from sys import platform
import os

def is_mac():
    return platform == "darwin"

def is_linux():
    return platform == "linux" or platform == "linux2"

def is_windows():
    return os.name == 'nt'

def relative_path(path, goback=0):
    levels = [".."] * (goback + -1)
    return os.path.abspath(os.path.join(os.getcwd(), *levels, path))



def retry(func, retry_wait=None, retries=5):
    tries = 0
    while tries < retries:
        tries += 1
        try:
            created_result = func()
            return created_result
        except Exception as e:

            traceback.print_exc()

            if tries == retries:
                raise e

            print('Retrying')

            if retry_wait is not None:
                sleep(retry_wait)


def is_errors_instance(instances, error):
    for i in range(len(instances)):
        ins = instances[i]
        if isinstance(error, ins):
            return True, i
    return False, -1


def istuple(el):
    return type(el) is tuple


def ignore_errors(func, instances=None):
    try:
        created_result = func()
        return created_result
    except Exception as e:
        is_valid_error, index = is_errors_instance(
            instances, e)
        if not is_valid_error:
            raise e
        print('Ignoring')
        traceback.print_exc()


def retry_if_is_error(func, instances=None, retries=2, wait_time=None):
    tries = 0
    errors_only_instances = list(
        map(lambda el: el[0] if istuple(el) else el, instances))

    while tries < retries:
        tries += 1
        try:
            created_result = func()
            return created_result
        except Exception as e:
            is_valid_error, index = is_errors_instance(
                errors_only_instances, e)

            if not is_valid_error:
                raise e

            traceback.print_exc()

            if istuple(instances[index]):
                instances[index][1]()

            if tries == retries:
                raise e

            print('Retrying')

            if wait_time is not None:
                sleep(wait_time)


def keep_doing(func, wait=1):
    while True:
        func()
        sleep(wait)


def silentremove(filename):
    try:
        os.remove(filename)
        return True
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise
        else:
            return False

def get_range(_from, _to):
    return ",".join(map(str, list(range(_from, _to))))


def find_by_key(ls,  key, value):
    for index in range(len(ls)):
        user = ls[index]
        if user[key] == value:
            return user


def find_by_id(ls, id):
    return find_by_key(ls, 'id', id)


def remove_nones(list):
    return [element for element in list if element is not None]





def exit_with_failed_status():
    print('Exiting with status 1')
    sys.exit(1)




def sleep_for_n_seconds(n):
    print(f"Sleeping for {n} seconds...")
    sleep(n)


def on_exception(f, on_exception):
    try:
        f()
    except Exception as e:
        print(e)
        on_exception()


def merge_list_of_dicts(*dicts):
    result = []
    for i in range(len(dicts[0])):
        el = {}
        for each_dict in dicts:
            el.update(each_dict[i])
        result.append(el)
    return result


def merge_dicts_in_one_dict(*dicts):
    el = {}
    for each_dict in dicts:
        el.update(each_dict)
    return el


def wrap_with_dict(ls, key):
    def wrap(i):
        return {f'{key}': i}
    return list(map(wrap, ls))


def delete_from_dicts(ls, key):
    for x in ls:
        x.pop(key)
    return ls


def extract_from_dict(ls, key):
    return list(map(lambda i: i[key], ls))



def get_boolean_variable(name: str, default_value: bool = None):
    # Add more entries if you want, like: `y`, `yes`, ...
    true_ = ('True', 'true', '1', 't')
    false_ = ('False', 'false', '0', 'f')
    value = os.getenv(name, None)
    if value is None:
        if default_value is None:
            raise ValueError(f'Variable `{name}` not set!')
        else:
            value = str(default_value)
    if value.lower() not in true_ + false_:
        raise ValueError(f'Invalid value `{value}` for variable `{name}`')
    return value in true_


def pretty_print(result):
    print(json.dumps(result, indent=4))


def sleep_forever():
    print('Sleeping Forever')
    while True:
        sleep(100)


def flatten(l):
    return [item for sublist in l for item in sublist]


def is_error(errs):
    def fn(e):
        result, index = is_errors_instance(errs, e)
        return result
    return fn

NETWORK_ERRORS = [RemoteDisconnected, URLError,
                  ConnectionAbortedError, ContentTooShortError,  BlockingIOError]

is_network_error = is_error(NETWORK_ERRORS)

def pretty_format_time(time):
   return time.strftime("%H:%M:%S, %d %B %Y").replace(" 0", " ").lstrip("0")



def write_html( data, path,):
    with open(path, 'w', encoding="utf-8") as fp:
        fp.write(data)


def write_file( data, path,):
    with open(path, 'w', encoding="utf-8") as fp:
        fp.write(data)


def read_json(path):
    with open(path, 'r') as fp:
        users = json.load(fp)
        return users
    
def write_json(data, path,  indent=4):
    with open(path, 'w') as fp:
        json.dump(data, fp, indent=indent)


def get_driver_path():
    executable_name = "chromedriver.exe" if is_windows() else "chromedriver"
    dest_path = f"build/{executable_name}"
    return dest_path


datetime_format = '%Y-%m-%d %H:%M:%S'

def str_to_datetime(when):
    return datetime.strptime(
        when, datetime_format)


def datetime_to_str(when):
    return when.strftime(datetime_format)


