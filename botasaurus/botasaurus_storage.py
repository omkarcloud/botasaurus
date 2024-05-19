import os
import json

def relative_path(path, goback=0):
    levels = [".."] * (goback + -1)
    return os.path.abspath(os.path.join(os.getcwd(), *levels, path.strip()))

def get_cache_file_path() -> str:
    dr = os.path.abspath(os.path.join(os.path.dirname(__file__),  'botasaurus_storage.json'))
    return dr

class localStoragePyStorageException(Exception):
    pass


class BasicStorageBackend:
    def raise_dummy_exception(self):
        raise localStoragePyStorageException("Called dummy backend!")

    def get_item(self, item: str, default:any = None) -> str:
        self.raise_dummy_exception()

    def set_item(self, item: str, value: any) -> None:
        self.raise_dummy_exception()

    def remove_item(self, item: str) -> None:
        self.raise_dummy_exception()

    def clear(self) -> None:
        self.raise_dummy_exception()

class JSONStorageBackend(BasicStorageBackend):
    def __init__(self) -> None:
        self.refresh()

    def refresh(self):
        self.json_path = get_cache_file_path()
        self.json_data = {}

        if not os.path.isfile(self.json_path):
            self.commit_to_disk()

        with open(self.json_path, "r") as json_file:
            self.json_data = json.load(json_file)
        
    def commit_to_disk(self):
        with open(self.json_path, "w") as json_file:
            json.dump(self.json_data, json_file, indent=4)

    def get_item(self, key: str, default = None) -> str:
        if key in self.json_data:
            return self.json_data[key]
        return default


    def items(self):
        return self.json_data

    def set_item(self, key: str, value: any) -> None:
        self.json_data[key] = value
        self.commit_to_disk()

    def remove_item(self, key: str) -> None: 
        if key in self.json_data:
            self.json_data.pop(key)
            self.commit_to_disk()


    def clear(self) -> None:
        if os.path.isfile(self.json_path):
            os.remove(self.json_path)
        self.json_data = {}
        self.commit_to_disk()
    
class _LocalStorage:
    def __init__(self) -> None:
        self.storage_backend_instance = JSONStorageBackend()

    def refresh(self) -> None:
        self.storage_backend_instance.refresh()
    
    def get_item(self, item: str, default = None) -> any:
        return self.storage_backend_instance.get_item(item, default)

    def set_item(self, item: str, value: any) -> None:
        self.storage_backend_instance.set_item(item, value)

    def remove_item(self, item: str) -> None:
        self.storage_backend_instance.remove_item(item)

    def clear(self):
        self.storage_backend_instance.clear()

    def items(self):
        return self.storage_backend_instance.items()


_storage = None

# Create fn called get_package_storage which instantiates the PackageStorage class and returns it if not instantiated 
def get_botasaurus_storage():
    global _storage
    if not _storage:
        _storage = _LocalStorage()
    return _storage
