from .errors import JsonHTTPResponse, JsonHTTPResponseWithMessage
from .server import Server, get_scraper_error_message


def serialize(data):
    if data is None:
        return None
    if isinstance(data, list):
        return [item.to_json() for item in data]
    return data.to_json()

def create_task_not_found_error(task_id):
    return JsonHTTPResponse(
        {"status": 404, "message": f"Task {task_id} not found"}, status=404
    )


def deep_clone_dict(original_dict):
    if not isinstance(original_dict, dict):
        return original_dict

    new_dict = {}
    for key, value in original_dict.items():
        if isinstance(value, dict):
            new_dict[key] = deep_clone_dict(value)
        elif isinstance(value, list):
            new_dict[key] = [deep_clone_dict(item) for item in value]
        else:
            new_dict[key] = value

    return new_dict

def dict_to_string(errors_dict):
    # Iterate through each key-value pair in the dictionary
    formatted_pairs = []
    for key, values in errors_dict.items():
        # Join the list of strings into a single string with semicolon and space
        value_str = "; ".join(values)
        # Format the key and the joined string
        formatted_pair = f"{key}: {value_str}"
        formatted_pairs.append(formatted_pair)

    # Join the formatted pairs with a comma and a newline
    result_string = ", \n".join(formatted_pairs)

    return result_string


def is_string_of_min_length(data, min_length=1):
    """Checks if data is a string with a minimum length."""
    return isinstance(data, str) and len(data) >= min_length

def ensure_json_body_is_dict(json_data):
    if json_data is None:
        raise JsonHTTPResponseWithMessage("json body must be provided")

    if not isinstance(json_data, dict):
        raise JsonHTTPResponseWithMessage("json body must be provided as an object")

def validate_scraper_name(scraper_name):
    valid_scraper_names = Server.get_scrapers_names()
    valid_names_string = ', '.join(valid_scraper_names)

    if len(valid_scraper_names) == 0:
        error_message = get_scraper_error_message(valid_scraper_names, scraper_name, valid_names_string)
        raise JsonHTTPResponseWithMessage(error_message)

    if scraper_name is None:
        if len(valid_scraper_names) == 1:
            scraper_name = valid_scraper_names[0]
        else:
            error_message = f"'scraper_name' must be provided when there are multiple scrapers. The scraper_name must be one of {valid_names_string}."
            raise JsonHTTPResponseWithMessage(error_message)
    elif not Server.get_scraper(scraper_name):
        error_message = get_scraper_error_message(valid_scraper_names, scraper_name, valid_names_string)
        raise JsonHTTPResponseWithMessage(error_message)

    return scraper_name

def validate_task_request(json_data):
    """Validates the task request data."""

    ensure_json_body_is_dict(json_data)

    scraper_name = json_data.get("scraper_name")
    data = json_data.get("data")

    scraper_name = validate_scraper_name(scraper_name)

    if data is None:
        raise JsonHTTPResponseWithMessage("'data' key must be provided")

    if not isinstance(data, dict):
        raise JsonHTTPResponseWithMessage("'data' key must be a valid JSON object")

    controls = Server.get_controls(scraper_name)

    result = controls.getBackendValidationResult(data, timeout=300).valueOf()

    errors = result["errors"]

    if errors != {}:
        raise JsonHTTPResponseWithMessage(dict_to_string(errors))

    data = result["data"]
    metadata = result["metadata"]
    return scraper_name, data, metadata

def is_valid_positive_integer(param):
    try:
        return int(param) > 0
    except (ValueError, TypeError):
        return False

def is_valid_positive_integer_including_zero(param):
    try:
        return int(param) >= 0
    except (ValueError, TypeError):
        return False

def validate_filters(json_data):
    filters = json_data.get("filters")
    if filters:  # Only validate if it exists
        if not isinstance(filters, dict):
            raise JsonHTTPResponseWithMessage("Filters must be a dictionary")
    return filters

def validate_view(json_data, allowed_views):
    view = json_data.get("view")

    if view:
        if not is_string_of_min_length(view):
            raise JsonHTTPResponseWithMessage(
                "View must be a string with at least one character"
            )

        view = view.lower()
        if view not in allowed_views:
            raise JsonHTTPResponseWithMessage(
                f"Invalid view. Must be one of: {', '.join(allowed_views)}."
            )

    return view

def validate_sort(json_data, allowed_sorts, default_sort):
    sort = json_data.get("sort", default_sort)

    if sort == "no_sort":
        sort = None
    elif sort:
        if not is_string_of_min_length(sort):
            raise JsonHTTPResponseWithMessage(
                "Sort must be a string with at least one character"
            )

        sort = sort.lower()
        if sort not in allowed_sorts:
            raise JsonHTTPResponseWithMessage(
                f"Invalid sort. Must be one of: {', '.join(allowed_sorts)}."
            )
    else:
        sort = default_sort
    return sort

def validate_results_request(json_data, allowed_sorts, allowed_views, default_sort):
    """Validates parameters for a task results request (excluding format)."""

    ensure_json_body_is_dict(json_data)  # Assuming you have this helper

    # Filters Validation (if applicable)
    filters = validate_filters(json_data)

    # Sort Validation (if applicable)
    sort = validate_sort(json_data, allowed_sorts, default_sort)
    # View Validation (if applicable)
    view = validate_view(json_data, allowed_views)

    # Offset Validation
    page = json_data.get("page")
    if page is not None:
        try:
            page = int(page)
        except ValueError:
            raise JsonHTTPResponseWithMessage("page must be an integer")
        if not is_valid_positive_integer(page):
            raise JsonHTTPResponseWithMessage("page must be greater than or equal to 1")
    else:
        page = 1

    per_page = json_data.get("per_page")
    if per_page is not None:
        try:
            per_page = int(per_page)
        except ValueError:
            raise JsonHTTPResponseWithMessage("per_page must be an integer")
        if not is_valid_positive_integer(per_page):
            raise JsonHTTPResponseWithMessage(
                "per_page must be greater than or equal to 1"
            )

    return filters, sort, view, page, per_page

def validate_download_params(json_data, allowed_sorts, allowed_views, default_sort):
    """Validates download parameters for a task."""

    ensure_json_body_is_dict(json_data)

    # Format Validation
    fmt = json_data.get("format")

    if not fmt:
        fmt = "json"
    elif not is_string_of_min_length(fmt):  # Assuming you have this helper function
        raise JsonHTTPResponseWithMessage(
            "Format must be a string with at least one character"
        )
    elif fmt == "xlsx":
        fmt = "excel"

    fmt = fmt.lower()
    if fmt not in ["json", "csv", "excel"]:
        raise JsonHTTPResponseWithMessage(
            "Invalid format.  Must be one of: JSON, CSV, Excel"
        )

    # Filters Validation (if applicable)
    filters = validate_filters(json_data)

    # Sort Validation (if applicable)
    sort = validate_sort(json_data, allowed_sorts, default_sort)
    # View Validation (if applicable)
    view = validate_view(json_data, allowed_views)

    # Convert to English Validation (if applicable)
    convert_to_english = json_data.get("convert_to_english", True)
    if not isinstance(convert_to_english, bool):
        raise JsonHTTPResponseWithMessage("convert_to_english must be a boolean")

    return fmt, filters, sort, view, convert_to_english

def is_list_of_integers(obj):
    return isinstance(obj, list) and all(isinstance(item, int) for item in obj)

def validate_patch_task(json_data):
    ensure_json_body_is_dict(json_data)

    task_ids = json_data.get("task_ids")

    if not task_ids:
        raise JsonHTTPResponseWithMessage("'task_ids' must be provided")

    if not is_list_of_integers(task_ids):
        raise JsonHTTPResponseWithMessage("'task_ids' must be a list of integers")

    return task_ids

def validate_ui_patch_task(json_data):
    ensure_json_body_is_dict(json_data)

    action = json_data.get("action")
    task_ids = json_data.get("task_ids")

    if not action:
        raise JsonHTTPResponseWithMessage("'action' must be provided")

    if not isinstance(action, str):
        raise JsonHTTPResponseWithMessage("'action' must be a string")
    action = action.lower()
    if action not in ["abort", "delete"]:
        raise JsonHTTPResponseWithMessage('\'action\' must be either "abort" or "delete"')

    if not task_ids:
        raise JsonHTTPResponseWithMessage("'task_ids' must be provided")

    if not is_list_of_integers(task_ids):
        raise JsonHTTPResponseWithMessage("'task_ids' must be a list of integers")

    return action, task_ids