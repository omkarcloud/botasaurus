from random import shuffle
import functools
from urllib.parse import urlparse, urlunparse
from typing import Union, List
from .output import write_json
from .request_decorator import request

default_request_options = {
    # "use_stealth": True,
    "raise_exception": True,
    "create_error_logs": False,
    "close_on_crash": True,
    "output": None,
}


def remove_function_key(data_list):
    """
    Removes the 'function' key from each dictionary in the list.

    :param data_list: List of dictionaries, each potentially containing a 'function' key.
    :return: A new list of dictionaries, each without the 'function' key.
    """
    return [
        {key: value for key, value in item.items() if key != "function"}
        for item in data_list
    ]


def unique_keys(all_urls):
    return list(dict.fromkeys(all_urls))


def extractor_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Call the original function to get the filter function
        decorator_func = func(*args, **kwargs)

        # Return the structured dictionary
        return {
            "function_name": func.__name__,
            "arguments": [args, kwargs],
            "function": decorator_func,
        }

    return wrapper


def filter_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Call the original function to get the filter function
        filter_func = func(*args, **kwargs)

        # Return the structured dictionary
        return {
            "function_name": func.__name__,
            "arguments": [args, kwargs],
            "function": filter_func,
        }

    return wrapper


def extract_link_upto_nth_segment(n, url):
    parsed_url = urlparse(url)
    path_segments = parsed_url.path.strip("/").split("/")[:n]
    new_path = "/".join(path_segments)

    # Check if the original URL ends with a slash and adjust the new path accordingly

    if not new_path:
        new_path = "/"

    if parsed_url.path.endswith("/"):
        new_path = new_path.rstrip("/") + "/"

    # Reconstruct the URL up to the nth segment, preserving the trailing slash if present
    return urlunparse((parsed_url.scheme, parsed_url.netloc, new_path, "", "", ""))


class Filters:

    @staticmethod
    @filter_decorator
    def has_exactly_n_segments(n):
        def filter_func(url):
            path = urlparse(url).path.strip("/")
            segments = path.split("/") if path else []
            return len(segments) == n

        return filter_func

    @staticmethod
    def has_exactly_1_segment():
        return Filters.has_exactly_n_segments(1)

    @staticmethod
    def has_exactly_2_segments():
        return Filters.has_exactly_n_segments(2)

    @staticmethod
    def has_exactly_3_segments():
        return Filters.has_exactly_n_segments(3)

    @staticmethod
    @filter_decorator
    def has_at_least_n_segments(n):
        def filter_func(url):
            path = urlparse(url).path.strip("/")
            segments = path.split("/") if path else []
            return len(segments) >= n

        return filter_func

    @staticmethod
    def has_at_least_1_segment():
        return Filters.has_at_least_n_segments(1)

    @staticmethod
    def has_at_least_2_segments():
        return Filters.has_at_least_n_segments(2)

    @staticmethod
    def has_at_least_3_segments():
        return Filters.has_at_least_n_segments(3)

    @staticmethod
    @filter_decorator
    def has_at_most_n_segments(n):
        def filter_func(url):
            path = urlparse(url).path.strip("/")
            segments = path.split("/") if path else []
            return len(segments) <= n

        return filter_func

    @staticmethod
    def has_at_most_1_segment():
        return Filters.has_at_most_n_segments(1)

    @staticmethod
    def has_at_most_2_segments():
        return Filters.has_at_most_n_segments(2)

    @staticmethod
    def has_at_most_3_segments():
        return Filters.has_at_most_n_segments(3)

    @staticmethod
    @filter_decorator
    def nth_segment_equals(n: int, value: Union[str, List[str]]):
        def filter_func(url):
            path = urlparse(url).path.strip("/")
            segments = path.split("/") if path else []
            if 0 <= n < len(segments):
                if isinstance(value, list):  # Check if value is a list
                    return (
                        segments[n] in value
                    )  # Return True if nth segment matches any string in the list
                return segments[n] == value
            return False

        return filter_func

    @staticmethod
    def first_segment_equals(value: Union[str, List[str]]):
        return Filters.nth_segment_equals(0, value)

    @staticmethod
    def second_segment_equals(value: Union[str, List[str]]):
        return Filters.nth_segment_equals(1, value)

    @staticmethod
    def third_segment_equals(value: Union[str, List[str]]):
        return Filters.nth_segment_equals(2, value)

    @staticmethod
    @filter_decorator
    def last_segment_equals(value: Union[str, List[str]]):
        def filter_func(url):
            path = urlparse(url).path.strip("/")
            segments = path.split("/") if path else []
            return segments[-1] == value if segments else False

        return filter_func

    @staticmethod
    @filter_decorator
    def nth_segment_not_equals(n: int, value: Union[str, List[str]]):
        def filter_func(url):
            path = urlparse(url).path.strip("/")
            segments = path.split("/") if path else []
            if 0 <= n < len(segments):
                if isinstance(value, list):  # Check if value is a list
                    return (
                        segments[n] not in value
                    )  # Return True if nth segment does not match any string in the list
                return segments[n] != value
            return True

        return filter_func

    @staticmethod
    def first_segment_not_equals(value: Union[str, List[str]]):
        return Filters.nth_segment_not_equals(0, value)

    @staticmethod
    def second_segment_not_equals(value: Union[str, List[str]]):
        return Filters.nth_segment_not_equals(1, value)

    @staticmethod
    def third_segment_not_equals(value: Union[str, List[str]]):
        return Filters.nth_segment_not_equals(2, value)

    @staticmethod
    @filter_decorator
    def last_segment_not_equals(value: Union[str, List[str]]):
        def filter_func(url):
            path = urlparse(url).path.strip("/")
            segments = path.split("/") if path else []
            if segments:
                if isinstance(value, list):  # Check if value is a list
                    return (
                        segments[-1] not in value
                    )  # Return True if nth segment matches any string in the list
                return segments[-1] != value
            else:
                return True

        return filter_func

    @staticmethod
    @filter_decorator
    def any_segment_equals(value: Union[str, List[str]]):
        def filter_func(url):
            path = urlparse(url).path.strip("/")
            segments = path.split("/") if path else []
            if isinstance(value, list):  # Check if value is a list
                # Return True if any of the segments matches any string in the list
                return any(segment in value for segment in segments)
            return (
                value in segments
            )  # Check if value is in segments for a single string

        return filter_func

    @staticmethod
    @filter_decorator
    def domain_equals(domain: Union[str, List[str]]):
        def filter_func(url):
            netloc = urlparse(url).netloc
            if isinstance(domain, list):  # Check if domain is a list
                return (
                    netloc in domain
                )  # Return True if netloc matches any domain in the list
            return netloc == domain  # Check for a single domain string

        return filter_func

    @staticmethod
    @filter_decorator
    def domain_not_equals(domain: Union[str, List[str]]):
        def filter_func(url):
            netloc = urlparse(url).netloc
            if isinstance(domain, list):  # Check if domain is a list
                return (
                    netloc not in domain
                )  # Return True if netloc does not match any domain in the list
            return netloc != domain  # Check for a single domain string

        return filter_func


class Extractors:

    @staticmethod
    @extractor_decorator
    def extract_nth_segment(n):
        def extractor_func(url):
            path = urlparse(url).path.strip("/")
            segments = path.split("/") if path else []
            if 0 <= n < len(segments):
                return segments[n]
            return None

        return extractor_func

    @staticmethod
    def extract_first_segment():
        return Extractors.extract_nth_segment(0)

    @staticmethod
    def extract_second_segment():
        return Extractors.extract_nth_segment(1)

    @staticmethod
    def extract_third_segment():
        return Extractors.extract_nth_segment(2)

    @staticmethod
    @extractor_decorator
    def extract_last_segment():
        def extractor_func(url):
            path = urlparse(url).path.strip("/")
            segments = path.split("/") if path else []
            if segments:
                return segments[-1]
            return None

        return extractor_func

    @staticmethod
    @extractor_decorator
    def extract_link_upto_nth_segment(n):
        def extractor_func(url):
            return extract_link_upto_nth_segment(n, url)

        return extractor_func

    @staticmethod
    def extract_link_upto_first_segment():
        return Extractors.extract_link_upto_nth_segment(1)

    @staticmethod
    def extract_link_upto_second_segment():
        return Extractors.extract_link_upto_nth_segment(2)

    @staticmethod
    def extract_link_upto_third_segment():
        return Extractors.extract_link_upto_nth_segment(3)


def apply_filters_maps_sorts_randomize(
    request_options,
    urls,
    filters,
    extractors,
    sort_links,
    randomize_links,
):

    @request(**request_options)
    def sitemap(req, _):
        nonlocal urls

        filtered_urls = []
        for url in urls:
            passes_filters = True
            for filter_info in filters:
                filter_func = filter_info["function"]
                if not filter_func(url):
                    passes_filters = False
                    break
            if passes_filters:
                filtered_urls.append(url)

        extracted_urls = []
        for url in filtered_urls:
            transformed_url = url
            for map_info in extractors:
                extract_func = map_info["function"]
                transformed_url = extract_func(
                    transformed_url
                )  # Apply each extract function in turn
            extracted_urls.append(
                transformed_url
            )  # Add the final transformed URL to the new list

        urls = extracted_urls

        all_urls = unique_keys(urls)

        if sort_links:
            all_urls.sort()
        elif randomize_links:
            shuffle(all_urls)
        return all_urls

    filters_without_function = remove_function_key(filters)
    extractors_without_function = remove_function_key(extractors)

    data = {
        "filters": filters_without_function,
        "extractors": extractors_without_function,
        "sort_links": sort_links,
        "randomize_links": randomize_links,
        "urls": urls,
    }

    return sitemap(
        data,
    )


class _Base:
    def filter(self, *filter_funcs):
        for func in filter_funcs:
            if callable(func):  # Check if the argument is a function
                # Raise an exception with a helpful message
                raise Exception(
                    f"Kindly check the filter '{func.__name__}' and see if you forgot to call it."
                )

        self.filters.extend(
            filter_funcs
        )  # Extend the filters list only if all checks pass

        return self  # Allow chaining

    def extract(self, *extractor_funcs):
        for func in extractor_funcs:
            if callable(func):  # Check if the argument is a function
                # Raise an exception with a helpful message
                raise Exception(
                    f"Kindly check the extractor '{func.__name__}' and see if you forgot to call it."
                )

        self.extractors.extend(
            extractor_funcs
        )  # Extend the extractors list only if all checks pass

        return self  # Allow chaining for extractors

    def sort(self):
        self.sort_links = True
        self.randomize_links = False  # Ensure randomize is not set if sort is called
        return self  # Allow chaining

    def randomize(self):
        self.randomize_links = True
        self.sort_links = False  # Ensure sort is not set if randomize is called
        return self  # Allow chaining


class Links(_Base):

    def __init__(
        self,
        urls,
    ):
        self.filters = []  # Existing filters list
        self.extractors = []  # New list for extractors
        self.sort_links = False  # Flag for sorting links
        self.randomize_links = False  # Flag for randomizing links

        urls = urls if isinstance(urls, list) else [urls]

        self.urls = urls

    def get(self):
        # This function should be defined or imported in your code
        result = apply_filters_maps_sorts_randomize(
            {
                **default_request_options,
                "parallel": 40,
                "cache": False,
            },
            self.urls,
            self.filters,
            self.extractors,
            self.sort_links,
            self.randomize_links,
        )

        return result

    def write(self, filename: str):
        results = self.get()
        write_json(results, filename)
        return results