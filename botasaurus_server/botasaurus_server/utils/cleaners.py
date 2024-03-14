from botasaurus.output import get_fieldnames

def normalize_data(data):
    if data is None:
        return []
    elif isinstance(data, (list, set, tuple)):
        normalized_list = []
        for item in data:
            if item is None:
                continue  # Skip None items
            elif not isinstance(item, dict):
                item = {"data": item}  # Wrap non-dict items
            normalized_list.append(item)
        return normalized_list

    elif isinstance(data, dict):
        return [data]

    else:
        return [{"data": data}]
    
def normalize_dicts_by_fieldnames(data):
    fieldnames = get_fieldnames(data)
    filtered_data = []

    for item in data:
        filtered_item = {key: item.get(key, None) for key in fieldnames}
        filtered_data.append(filtered_item)

    return filtered_data

def clean_data(data):
    # Then, filter the normalized data to ensure each dict contains the same set of fieldnames
    return normalize_dicts_by_fieldnames(normalize_data(data))
