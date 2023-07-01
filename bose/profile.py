import random as random_module
from datetime import datetime
import os
import json
from .utils import datetime_to_str, relative_path, str_to_datetime

class ProfilePyStorageException(Exception):
    pass

class BasicStorageBackend:
    def raise_dummy_exception(self):
        raise ProfilePyStorageException("Called dummy backend!")

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
        self.json_path = relative_path( "profiles.json", 0)
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
        if 'created_at' not in value:
            value['created_at'] = datetime_to_str(datetime.now())

        value['updated_at'] = datetime_to_str(datetime.now())

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
    
class _Profile:
    def __init__(self) -> None:
        self.storage_backend_instance = JSONStorageBackend()

    profile = None
    def refresh(self) -> None:
        self.storage_backend_instance.refresh()

    def check_profile(self) -> None:
        if self.profile is None:
            raise Exception('This method can only be run in run method of Task and when you have given the current profile in the Browser Config.')

    def get_item(self, item: str, default = None) -> any:
        self.check_profile()
        profile = self.storage_backend_instance.get_item(self.profile, {})

        if default is None:
            return profile.get(item)
        else: 
            return profile.get(item, default)

    def set_item(self, item: str, value: any) -> None:
        self.check_profile()
        profile = self.storage_backend_instance.get_item(self.profile, {})
        profile[item] = value

        self.storage_backend_instance.set_item(self.profile, profile)

    def remove_item(self, item: str) -> None:
        self.check_profile()
        profile = self.storage_backend_instance.get_item(self.profile, {})
        del profile[item] 

        self.storage_backend_instance.set_item(self.profile, profile)

    def clear(self):
        self.check_profile()
        self.storage_backend_instance.remove_item(self.profile)

    def items(self):
        self.check_profile()
        profile = self.storage_backend_instance.get_item(self.profile, {})
        return profile

    def get_profiles(self, random = False):
        data = list(self.storage_backend_instance.items().values())
        
        if len(data) == 0:
            return data

        if (data[0].get('created_at') is None):
            if random:
                random_module.shuffle(data)
            return data
        
        if random:
            random_module.shuffle(data)
        else: 
            data =  sorted(data, key=lambda x: str_to_datetime(x['created_at']))

        return data

    def set_profile(self, profile):
        self.check_profile()
        if type(profile) is dict:
            self.storage_backend_instance.set_item(self.profile, profile)
        else: 
            raise Exception("Profile is not a dictionary.")

Profile = _Profile()

if __name__ == "__main__":
    t = _Profile()
    
    print(t.get_item("a"))
    print(t.set_item("a" ,"ss"))
    print(t.remove_item("a"))
