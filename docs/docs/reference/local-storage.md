---
sidebar_position: 80
---
# Local Storage

The LocalStorage module provides a way to persist data across Selenium browser runs. It stores data in a file named local_storage.json, which is created in the root directory of the project. The module provides methods to set, get, remove, and clear items from the local storage.

Class: LocalStorage

-   get_item(item: str, default = None) -> any: Retrieves an item from the local storage with the specified key. If the item does not exist, returns the default value (which defaults to None).
-   set_item(item: str, value: any) -> None: Adds or updates an item in the local storage with the specified key and value.
-   remove_item(item: str) -> None: Removes an item from the local storage with the specified key.
-   clear(): Removes all items from the local storage.

## Usage

```python 
from bose import LocalStorage

# Set an item in the Local Storage
LocalStorage.set_item('username', 'johndoe')

# Retrieve an item from the Local Storage
username = LocalStorage.get_item('username')

# Remove an item from the Local Storage
LocalStorage.remove_item('username')

# Clear all items from the Local Storage
LocalStorage.clear()
```