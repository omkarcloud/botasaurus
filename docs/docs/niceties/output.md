---
sidebar_position: 40
---

# Output

In Bose, you can save scraped data as CSV or JSON files by returning them from the `run` method of the driver. 

The data will be automatically saved in the output folder as json and csv file.

```python
from bose import *
        
class Task(BaseTask):
    def run(self, driver):
        return [{"name": "John Doe", "age": 42}]
```

**However, in some cases, you need more control over how the data is saved, such as when organizing it by date or author.**

In such cases, you can use the `Output` module to read and write data in JSON or CSV format.

## Saving CSV

The following example shows how to save data as a CSV file:

```python
from bose import Output

# Data to be written to the file
data = [
    {"name": "John Doe", "age": 42},
    {"name": "Jane Smith", "age": 27},
    {"name": "Bob Johnson", "age": 35}
]

# Write the data to the file "data.csv"
Output.write_csv(data, "data.csv")
```

## Saving JSON

The following example saves data as a JSON file:

```python
from bose import Output

# Data to be written to the file
data = [
    {"name": "John Doe", "age": 42},
    {"name": "Jane Smith", "age": 27},
    {"name": "Bob Johnson", "age": 35}
]

# Write the data to the file "data.json"
Output.write_json(data, "data.json")
```

## Reading JSON

The following code shows how to read data from a JSON file:

```python
from bose import Output

# Read the contents of the file "data.json"
data = Output.read_json("data.json")

# Print the contents
print(data)
```
