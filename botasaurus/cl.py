import json
from typing import List

def snakecase(string: str, keep_together: List[str] = None) -> str:
    """Convert a string into snake_case.

    Args:
        string (:obj:`str`):
            The string to convert to snake_case.
        keep_together (:obj:`List[str]`, `optional`):
            (Upper) characters to not split, e.g., "HTTP".

    Returns:
        :obj:`str`: The snake_cased string.
    """
    import re
    if not string:
        return ""
    leading_underscore: bool = string[0] == "_"
    trailing_underscore: bool = string[-1] == "_"
    # If all uppercase, turn into lowercase
    if string.isupper():
        string = string.lower()
    if keep_together:
        for keep in keep_together:
            string = string.replace(keep, f"_{keep.lower()}_")
    # Manage separators
    string = re.sub(r"[\W]", "_", string)
    # Manage capital letters and numbers
    string = re.sub(r"([A-Z]|\d+)", r"_\1", string)
    # Add "_" after numbers
    string = re.sub(r"(\d+)", r"\1_", string).lower()
    # Remove repeated "_"
    string = re.sub(r"[_]{2,}", "_", string)
    string = re.sub(r"^_", "", string) if not leading_underscore else string
    return re.sub(r"_$", "", string) if not trailing_underscore else string

def camelcase(string: str) -> str:
    """Convert a string into camelCase.

    Args:
        string (:obj:`str`): 
            The string to convert to camelCase.

    Returns:
        :obj:`str`: The camelCased string.
    """
    import re
    if not string:
        return ""
    # Turn into snake_case, then remove "_" and capitalize first letter
    string = "".join(f"{s[0].upper()}{s[1:].lower()}"
                     for s in re.split(r'_', snakecase(string)) if s)
    # Make first letter lower
    return f"{string[0].lower()}{string[1:]}" if string else ""

def remove_commas(s):
    if isinstance(s, str):
        return s.replace(",", "")


def snakecase_keys(data):
    if isinstance(data, list):
        return [snakecase_keys(item) for item in data]
    elif isinstance(data, dict):
        return {snakecase(key): snakecase_keys(value) for key, value in data.items()}
    else:
        return data


def camelcase_keys(data):
    if isinstance(data, list):
        return [camelcase_keys(item) for item in data]
    elif isinstance(data, dict):
        return {camelcase(key): camelcase_keys(value) for key, value in data.items()}
    else:
        return data


def select(data, *keys, default=None, max_depth=None, map_data=None, filter_func=None):
    def _search(data, keys, current_depth):
        if not keys or (max_depth is not None and current_depth > max_depth):
            return None

        current_key = keys[0]
        remaining_keys = keys[1:]

        # Handling dictionaries
        if isinstance(data, dict):
            for k, v in data.items():
                if k == current_key:
                    if not remaining_keys:
                        if filter_func is None or filter_func(v):
                            return v
                    else:
                        return _search(v, remaining_keys, current_depth + 1)
                result = _search(v, keys, current_depth + 1)
                if result is not None:
                    return result

        # Handling lists
        elif isinstance(data, list):
            if isinstance(current_key, int):
                # Adjust negative index
                if current_key < 0:
                    current_key += len(data)

                if 0 <= current_key < len(data):
                    if not remaining_keys:
                        if filter_func is None or filter_func(data[current_key]):
                            return data[current_key]
                    else:
                        return _search(
                            data[current_key], remaining_keys, current_depth + 1
                        )
            else:
                for item in data:
                    result = _search(item, keys, current_depth + 1)
                    if result is not None:
                        return result

        return None

    if map_data is None:
        map_data = lambda x: x

    if not keys:
        result = map_data(data) if data is not None else default
        return result
    else:
        result = _search(data, keys, 0)
        result = map_data(result) if result is not None else default

    return result


# Implement Later
# def select_all(*args):
#     if None in args:
#         return None
#     return args


def extract_numbers(s):
    import re
    if isinstance(s, str):
        # Use regular expression to find all numbers in the text
        numbers = re.findall(r"\b\d+(?:\.\d+)?\b", remove_commas(s))
        # Convert the extracted strings to floats or integers
        return [float(num) if "." in num else int(num) for num in numbers]

    if isinstance(s, int) or isinstance(s, float):
        return [s]

    return []


def extract_number(s):
    import re
    if isinstance(s, str):
        # Use regular expression to find all numbers in the text
        numbers = re.findall(r"\b\d+(?:\.\d+)?\b", remove_commas(s))
        # Convert the extracted strings to floats or integers
        return select(
            [float(num) if "." in num else int(num) for num in numbers], 0, max_depth=1
        )

    if isinstance(s, int) or isinstance(s, float):
        return s

def extract_links(s):
    import re    
    if isinstance(s, str):
        return re.findall(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            s,
        )
    return []


def extract_emails(s):
    import re    
    if isinstance(s, str):
        email_regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        return re.findall(email_regex, s)
    return []


def extract_otps(s):
    import re    
    if isinstance(s, str):
        return re.findall(r"\b\d{4,6}\b", s)
    return []


def is_email_verification_link(link):
    link = extract_path_from_link(link)
    return any(
        token in link
        for token in [
            "token",
            "confirm",
            "pass",
            "reset",
            "otp",
            "code",
            "verify",
            "auth",
        ]
    )


def extract_email_verification_links(s):
    if isinstance(s, str):
        return [link for link in extract_links(s) if is_email_verification_link(link)]
    return []


def extract_ld_json(soup, filter):
    ld_json_tags = soup.find_all("script", type="application/ld+json")

    results = []
    for tag in ld_json_tags:
        try:
            ld_json = json.loads(tag.string)
            if filter is None:
                results.append(ld_json)
            elif isinstance(filter, str) and filter in ld_json:
                results.append(ld_json)
            elif (
                hasattr(filter, "__iter__")
                and len(filter) == 2
                and filter[0] in ld_json
                and ld_json[filter[0]] == filter[1]
            ):
                results.append(ld_json)
            elif callable(filter) and filter(ld_json):
                results.append(ld_json)
        except json.JSONDecodeError:
            continue

    return results


def extract_meta_content(soup, property_name):
    og_image_tag = soup.find("meta", property=property_name)

    # Extract the content attribute if the tag is found
    if og_image_tag and "content" in og_image_tag.attrs:
        return og_image_tag["content"]


def extract_path_from_link(link):
    from urllib.parse import urlparse, urlunparse    
    if isinstance(link, str):
        parsed = urlparse(link)
        return str(
            urlunparse(
                ("", "", parsed.path, "", "", "")
            )
        )


def extract_domain_from_link(link):
    from urllib.parse import urlparse    
    if isinstance(link, str):
        return urlparse(link).netloc


def wrap_in_dict(data, *args):
    if data is None or not args:
        return None
    result = data
    for arg in reversed(args):
        result = {arg: result}
    return result


def extract_from_dict(data, *args):
    if data is None:
        return None
    if isinstance(data, dict):
        return select(data, *args)
    elif isinstance(data, list):
        return [select(d, *args) for d in data]
    return []


def join_link(link, path=None, query_params=None):
    from urllib.parse import urlencode
    
    if path:
        prepend = link.rstrip("/")
        href = path.lstrip("/")

        link = f"{prepend}/{href}"
    else:
        link = link
        
    if query_params:
        query_params = urlencode(query_params)
        link = f"{link}?{query_params}"
    return link


def join_dicts(*dicts):
    if len(dicts) == 0:
        return {}

    def merge_dicts_in_one_dict(*dicts):
        el = {}
        for each_dict in dicts:
            if isinstance(each_dict, dict):
                el.update(each_dict)
        return el

    def merge_list_of_dicts(*dicts):
        result = []
        for i in range(len(dicts[0])):
            el = {}
            for each_dict in dicts:
                item = select(each_dict, i)
                if isinstance(item, dict):
                    el.update(item)
            result.append(el)
        return result

    if isinstance(dicts[0], dict):
        return merge_dicts_in_one_dict(*dicts)
    elif isinstance(dicts[0], list):
        return merge_list_of_dicts(*dicts)

    return {}


def join_with_commas(*args):
    return ", ".join(str(arg) for arg in args)


def join_with_newlines(*args):
    return "\n".join(str(arg) for arg in args)


def trim_and_collapse_spaces(s):
    import re    
    if isinstance(s, str):
        return re.sub(r"\s+", " ", s.strip())


def link_matches_path(link, path):
    if isinstance(link, dict):
        link = link.get("link", link.get("href", link.get("url")))

    if isinstance(link, str):
        return extract_path_from_link(link).strip("/").startswith(path.strip("/"))

    return False


def filter_links_by_path(links, path):
    if links is None or path is None:
        return None

    if len(links) == 0:
        return []

    if isinstance(links[0], dict):
        return [link for link in links if link_matches_path(link, path)]
    elif isinstance(links[0], str):
        return [link for link in links if link_matches_path(link, path)]


def pluralize(word, items):
    if word is None or items is None:
        return None

    return word if len(items) <= 1 else word + "s"


def flatten_list(list_of_lists):
    if isinstance(list_of_lists, list):
        do_flatten = (
            lambda l: sum(map(do_flatten, l), []) if isinstance(l, list) else [l]
        )
        return do_flatten(list_of_lists)

    return [list_of_lists]


def find_value_in_dict(obj, filter):
    for key in obj:
        if filter(key, obj[key]):
            return obj[key]


def sort_object_by_keys(obj, *ordered_keys, reverse=False):
    # Create an ordered dictionary
    ordered_obj = {}

    if reverse:
        # Add keys not in ordered_keys first
        for key in obj:
            if key not in ordered_keys:
                ordered_obj[key] = obj[key]
        # Then add ordered keys
        for key in ordered_keys:
            if key in obj:
                ordered_obj[key] = obj[key]
    else:
        # Original logic: add ordered keys first
        for key in ordered_keys:
            if key in obj:
                ordered_obj[key] = obj[key]
        # Then add any additional keys found in the original object
        for key in obj:
            if key not in ordered_obj:
                ordered_obj[key] = obj[key]

    return ordered_obj


def rename_keys(original_obj, renaming_map):
    # Create a new dictionary, preserving the order of the original keys
    renamed_obj = {}

    for key in original_obj:
        new_key = renaming_map.get(
            key, key
        )  # Use the new key if it exists in the renaming map, else use the original key
        renamed_obj[new_key] = original_obj[key]

    return renamed_obj


def base64_decode(encoded_str):
    from base64 import b64decode

    """
    Decodes a base64 encoded string.
    
    :param encoded_str: A base64 encoded string.
    :return: The decoded string.
    """
    # Decoding the base64 encoded string
    decoded_bytes = b64decode(encoded_str)
    # Converting the bytes to string
    decoded_str = decoded_bytes.decode("utf-8")

    return decoded_str
