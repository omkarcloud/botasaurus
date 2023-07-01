---
sidebar_position: 70
---
# Output

Output is a utility class that provides methods for writing data in file formats such as JSON, CSV, and Excel files.  

It also provides convenience methods for reading and writing specific files, that are used in web scraping. These are "pending.json" file which represends data that will be used for furthur processing and "finished.json" file which represends data that is the final clean output of scraping Task. 

Output Class reads/writes all data in `output/` folder of root directory. 

## Importing 
Before using the methods you need to import them as follows
```python
from bose import Output
```

## Methods


### `read_pending()`

Reads the contents of "output/pending.json" file and returns its contents as a Python object.

**Example**

```python
data = Output.read_pending()

# Print the contents
print(data)
```

### `write_pending(data)`

Writes a Python object to the "output/pending.json" file.

**Example**

```python
# Data to write to the file
data = [
    {"name": "John Doe", "age": 42},
    {"name": "Jane Smith", "age": 27},
    {"name": "Bob Johnson", "age": 35}
]

# Write the data to the file "pending.json"
Output.write_pending(data)
```


### `read_finished_json()`

Reads a JSON file in "output/finished.json" and returns its contents as a Python object.


**Example**

```python
data = Output.read_finished_json()

# Print the contents
print(data)
```

### `write_finished_json(data)`

Writes a Python object to the "output/finished.json" file.

**Example**

```python
# Data to write to the file
data = [
    {"name": "John Doe", "age": 42},
    {"name": "Jane Smith", "age": 27},
    {"name": "Bob Johnson", "age": 35}
]

# Write the data to the file "finished.json"
Output.write_finished_json(data)
```

### `read_json(filename)`

Reads a JSON file from 'output/' directory and returns its contents as a Python object.

**Example**

```python
# Read the contents of the file "output/data.json"
data = Output.read_json("data.json")

# Print the contents
print(data)`
```

### `write_json(data, filename)`

Writes a Python object to a JSON file in 'output/' directory.

**Example**

```python
# Data to write to the file
data = {
    "name": "John Doe",
    "age": 42,
    "email": "johndoe@example.com"
}

# Write the data to the file "data.json"
Output.write_json(data, "data.json")

# Confirm that the file was written
print("File written successfully!")
```

### `write_csv(data, filename)`

Writes a list of dictionaries to a CSV file in 'output/' directory.

**Example**

```python
# Data to write to the file
data = [
    {"name": "John Doe", "age": 42},
    {"name": "Jane Smith", "age": 27},
    {"name": "Bob Johnson", "age": 35}
]

# Write the data to the file "data.csv"
Output.write_csv(data, "data.csv")
```
### `write_xlsx(data, filename)`

Writes a list of dictionaries to an Excel file in 'output/' directory.

**Example**

```python
# Data to write to the file
data = [
    {"name": "John Doe", "age": 42},
    {"name": "Jane Smith", "age": 27},
    {"name": "Bob Johnson", "age": 35}
]

# Write the data to the file "data.xlsx"
Output.write_xlsx(data, "data.xlsx")
```
