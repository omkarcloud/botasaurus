

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

def asteriskText(inp):
    from random import randint
    from math import ceil    

    if not inp:  # Do nothing if no string passed
        return ""
    rep="*"

    arr = list(inp)  # Convert String to Array
    len_arr = len(arr)

    if len_arr <= 2:
        i = 1
    else:
        i = ceil(len_arr / 2) 

    i = min(i, len_arr)  # Ensure i doesn't exceed the array length

    done = set()
    while i > 0: 
        r = randint(0, len_arr - 1)
        if r in done:
            continue
        arr[r] = rep 
        done.add(r)
        i -= 1
    return "".join(arr)

def hide_text_with_asterisk(data, exceptKeys=[]):
    """
    Hides the text using asterisks, replacing characters with '*'.
    
    Args:
        data: The input data, which can be a dictionary, list, or string.
        exceptKeys (list): A list of keys to exclude from hiding in dictionaries.
    
    Returns:
        The data with the text hidden using asterisks.
    
    Examples:
        hide_text_with_asterisk("password")
        Output: "p*s*w**d"
        
        hide_text_with_asterisk({"username": "john", "password": "secret"}, exceptKeys=["username"])
        Output: {"username": "john", "password": "s*c**t"}
        
        hide_text_with_asterisk(["apple", "banana", "cherry"])
        Output: ["a*p*e", "b*n**a", "c*e**y"]
    """
    if isinstance(data, dict):
        exceptKeys_set = set(exceptKeys)
        return {key: applyTransformer(value, asteriskText) if key not in exceptKeys_set else value for key, value in data.items()}
    elif isinstance(data, list):
        return [hide_text_with_asterisk(element, exceptKeys) for element in data]
    elif isinstance(data, str):
        return asteriskText(data)
    else:
        return data

def ht(data, exceptKeys=[]):
    """
    Short alias for hide_text_with_asterisk().
    
    Args:
        data: The input data, which can be a dictionary, list, or string.
        exceptKeys (list): A list of keys to exclude from hiding in dictionaries.
    
    Returns:
        The data with the text hidden using asterisks.
    
    Examples:
        ht("password")
        Output: "p*s*w**d"
        
        ht({"username": "john", "password": "secret"}, exceptKeys=["username"])
        Output: {"username": "john", "password": "s*c**t"}
        
        ht(["apple", "banana", "cherry"])
        Output: ["a*p*e", "b*n**a", "c*e**y"]
    """
    return hide_text_with_asterisk(data, exceptKeys)