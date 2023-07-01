---
sidebar_position: 50
---

# Output Data As CSV/JSON


The following example demonstrates how to output data as CSV or JSON:

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

# Write the data to the file "data.csv"
Output.write_csv(data, "data.csv")
```