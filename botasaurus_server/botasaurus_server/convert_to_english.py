from unidecode import unidecode

def unicode_to_ascii(text):
    """
    Convert unicode text to ASCII, replacing special characters.
    """
    if text is None:
        return None

    # Replacing 'ë' with 'e' and return the ASCII text
    return unidecode(text).replace("ë", "e")


def applyTransformer(data, transformer):
    """
    Apply a transformer function to all strings in a nested data structure.

    :param data: The data structure (dict, list, nested dicts) to transform.
    :param transformer: A function that takes a string and returns a transformed string.
    :return: The transformed data structure.
    """
    if isinstance(data, dict):
        # If the item is a dictionary, apply the transformer to each value.
        return {key: applyTransformer(value, transformer) for key, value in data.items()}
    elif isinstance(data, list):
        # If the item is a list, apply the transformer to each element.
        return [applyTransformer(element, transformer) for element in data]
    elif isinstance(data, str):
        # If the item is a string, apply the transformer directly.
        return transformer(data)
    else:
        # If the item is not a dict, list, or string, return it as is.
        return data


def convert_unicode_dict_to_ascii_dict(data):
    """
    Convert unicode data to ASCII, replacing special characters.
    """
    return applyTransformer(data, unicode_to_ascii)
