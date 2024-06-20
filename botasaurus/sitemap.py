from random import shuffle
import re
import functools
from urllib.parse import urlparse, unquote_plus, urlunparse
from gzip import decompress
from typing import Union, List
from bs4 import BeautifulSoup

from .list_utils import flatten
from .cl import join_link
from .request_decorator import request

default_request_options = {
    # "use_stealth": True,
    "raise_exception": True,
    "create_error_logs": False,
    "close_on_crash": True,
    "output": None,
}


class GunzipException(Exception):
    """
    gunzip() exception.
    """

    pass


def gunzip(data) :
    """
    Decompresses gzipped data.

    :param data: Gzipped data as bytes.
    :return: Decompressed data as bytes.
    :raises GunzipException: If the input data is not valid or decompression fails.
    """

    if data is None:
        raise GunzipException("response data is None. Expected gzipped data as bytes.")

    if not isinstance(data, bytes):
        raise GunzipException(
            f"Invalid data type: {type(data).__name__}. Expected gzipped data as bytes."
        )

    if len(data) == 0:
        raise GunzipException(
            "response data is empty. Gzipped data cannot be an empty byte string."
        )

    try:
        gunzipped_data = decompress(data)
    except Exception as ex:
        raise GunzipException(f"Decompression failed. Error during gunzipping: {ex}")

    if gunzipped_data is None:
        raise GunzipException(
            "Decompression resulted in None. Expected decompressed data as bytes."
        )

    if not isinstance(gunzipped_data, bytes):
        raise GunzipException(
            "Decompression resulted in non-bytes data. Expected decompressed data as bytes."
        )

    gunzipped_data = gunzipped_data.decode("utf-8-sig", errors="replace")

    assert isinstance(gunzipped_data, str)

    return gunzipped_data


def isgzip(url, response):

    uri = urlparse(url)
    url_path = unquote_plus(uri.path)
    content_type = response.headers.get("content-type") or ""

    if url_path.lower().endswith(".gz") or "gzip" in content_type.lower():
        return True

    else:
        return False


@request(
    **default_request_options,
)
def fetch_content(request, url: str):
    """Fetch content from a URL, handling gzip if necessary."""
    response = request.get(url, timeout=30)
    status_code = response.status_code

    if status_code == 404:

        if url.endswith("robots.txt"):
            print("robots.txt not found (404) at the following URL: " + response.url)

        else:
            print("Sitemap not found (404) at the following URL: " + response.url)
        return None

    response.raise_for_status()

    if isgzip(url, response):
        return gunzip(response.content)
    else:
        return response.text


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
    return urlunparse(
        (parsed_url.scheme, parsed_url.netloc, new_path, "", "", "")
    )


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
                    return segments[n] in value  # Return True if nth segment matches any string in the list
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
                    return segments[n] not in value  # Return True if nth segment does not match any string in the list
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
            return segments[-1] != value if segments else True

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
            return value in segments  # Check if value is in segments for a single string

        return filter_func

    @staticmethod
    @filter_decorator
    def domain_equals(domain: Union[str, List[str]]):
        def filter_func(url):
            netloc = urlparse(url).netloc
            if isinstance(domain, list):  # Check if domain is a list
                return netloc in domain  # Return True if netloc matches any domain in the list
            return netloc == domain  # Check for a single domain string

        return filter_func

    @staticmethod
    @filter_decorator
    def domain_not_equals(domain: Union[str, List[str]]):
        def filter_func(url):
            netloc = urlparse(url).netloc
            if isinstance(domain, list):  # Check if domain is a list
                return netloc not in domain  # Return True if netloc does not match any domain in the list
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


def wrap_in_sitemap(urls):
    return [{"url":url, "type":"sitemap"} for url in urls]

def clean_sitemap_response(s, char='<'):
    # Find the index of the given character
    char_index = s.find(char)
    
    # If the character is not found, return the original string
    if char_index == -1:
        return s
    
    # Otherwise, return the substring starting from the character
    return s[char_index:]

def get_sitemaps_urls(request_options, urls):
    visited = set()

    @request(**request_options)
    def sitemap(req, data):

        nonlocal visited  # Reference the global visited set


        url = data.get("url")
        # [   if isinstance( data, dict)]:
        # If the URL has already been visited, return an empty list to prevent infinite recursion
        if url in visited:
            return []

        visited.add(url)

        content = clean_sitemap_response(fetch_content(url))
        if not content:
            return []

        locs = find_the_sitemaps(content)

        links = [url]

        parsed = sitemap(wrap_in_sitemap(locs))

        for x in parsed:
            links.extend(x)

        return links


    def find_the_sitemaps(content):
        root = BeautifulSoup(content, 'lxml-xml')

        locs = []
        # Look for sitemap entries, which indicate nested sitemaps
        for sm in root.select("sitemap"):
            el = sm.select_one("loc")
            if el is not None:
                locs.append(el.text.strip())

        return locs
    return sitemap(
        wrap_in_sitemap(urls)
    )


def get_urls(request_options, urls):
    visited = set()

    @request(**request_options)
    def sitemap(req, url):

        nonlocal visited  # Reference the global visited set

        # If the URL has already been visited, return an empty list to prevent infinite recursion
        if url in visited:
            return []

        visited.add(url)

        content = clean_sitemap_response(fetch_content(url))

        if not content:
            return []

        links, locs = get_links_sitemaps(content)

        parsed = sitemap(locs)

        for x in parsed:
            links.extend(x)

        return links


    def get_links_sitemaps(content):
        root = BeautifulSoup(content, 'lxml-xml')

        links = []
        # Look for URL entries, which indicate actual page links
        for url_entry in root.select("url"):
            loc = url_entry.select_one("loc")
            if loc is not None:
                links.append(loc.text.strip())
        # Look for sitemap entries, which indicate nested sitemaps
        locs = []
        for sm in root.select("sitemap"):
            el = sm.select_one("loc")
            if el is not None:
                locs.append(el.text.strip())

        return links, locs

    return sitemap(
        urls,
    )


def clean_robots_txt_url(url):
    return extract_link_upto_nth_segment(0, url) + "robots.txt"


def is_empty_path(url):
    return not urlparse(url).path.strip("/")


def get_sitemaps_from_robots(request_options, urls):
    visited = set()

    @request(**request_options)
    def sitemap(req, url):

        nonlocal visited  # Reference the global visited set

        # If the URL has already been visited, return an empty list to prevent infinite recursion
        if url in visited:
            return []

        visited.add(url)

        content = fetch_content(url)

        if not content:
            return []

        return parse_sitemaps_from_robots_txt(
            extract_link_upto_nth_segment(0, url), content
        )
    ls = []
    
    for url in urls:
        temp = sitemap(clean_robots_txt_url(url)) if is_empty_path(url) else url
        ls.append(temp)
    
    return flatten(
      ls  
    )


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
                transformed_url = extract_func(transformed_url)  # Apply each extract function in turn
            extracted_urls.append(transformed_url)  # Add the final transformed URL to the new list

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


def unique_keys(all_urls):
    return list(dict.fromkeys(all_urls))


def clean_url(base_url, url: str) -> bool:
    """
    Returns true if URL is of the "http" ("https") scheme.

    :param url: URL to test.
    :return: True if argument URL is of the "http" ("https") scheme.
    """
    if url is None:
        print("URL is None")
        return False
    if len(url) == 0:
        print("URL is empty")
        return False


    try:
        uri = urlparse(url)
        _ = urlunparse(uri)

    except Exception as ex:
        print(f"Cannot parse URL {url}: {ex}")
        return False

    if not uri.scheme:
        return join_link(base_url, url)

    if uri.scheme.lower() not in ["http", "https"]:
        return join_link(base_url, url)

    if not uri.hostname:
        return join_link(base_url, url)

    return url


def parse_sitemaps_from_robots_txt(base_url, robots_txt_content):
    """
    Parses sitemaps URLs from the content of a robots.txt file.

    :param robots_txt_content: The content of the robots.txt file as a string.
    :return: A list of unique sitemaps URLs found in the robots.txt content.
    """
    # Serves as an ordered set because we want to deduplicate URLs but also retain the order
    sitemap_urls = {}

    for robots_txt_line in robots_txt_content.splitlines():
        robots_txt_line = robots_txt_line.strip()
        # robots.txt is supposed to be case sensitive, but handling it case-insensitively here
        sitemap_match = re.search(
            r"^sitemap:\s*(.+?)$", robots_txt_line, flags=re.IGNORECASE
        )
        if sitemap_match:
            sitemap_url = sitemap_match.group(1)

            cleaned = clean_url(base_url, sitemap_url)
            if cleaned:
                sitemap_urls[cleaned] = True
            else:
                print(
                    f"Sitemap URL '{sitemap_url}' is not a valid URL, skipping"
                )

    return list(sitemap_urls.keys())


class Sitemap:
    def __init__(self, urls, cache=True):
        self.cache = cache
        self.filters = []  # Existing filters list
        self.extractors = []  # New list for extractors
        self.sort_links = False  # Flag for sorting links
        self.randomize_links = False  # Flag for randomizing links

        urls = urls if isinstance(urls, list) else [urls]

        urls = get_sitemaps_from_robots(self._create_request_options(), urls )
        self.urls = urls

    def filter(self, *filter_funcs):
        for func in filter_funcs:
            if callable(func):  # Check if the argument is a function
                # Raise an exception with a helpful message
                raise Exception(f"Kindly check the filter '{func.__name__}' and see if you forgot to call it.")
        
        self.filters.extend(filter_funcs)  # Extend the filters list only if all checks pass

        return self  # Allow chaining
    def extract(self, *extractor_funcs):
        for func in extractor_funcs:
            if callable(func):  # Check if the argument is a function
                # Raise an exception with a helpful message
                raise Exception(f"Kindly check the extractor '{func.__name__}' and see if you forgot to call it.")

        self.extractors.extend(extractor_funcs)  # Extend the extractors list only if all checks pass

        return self  # Allow chaining for extractors

    def sort(self):
        self.sort_links = True
        self.randomize_links = False  # Ensure randomize is not set if sort is called
        return self  # Allow chaining

    def randomize(self):
        self.randomize_links = True
        self.sort_links = False  # Ensure sort is not set if randomize is called
        return self  # Allow chaining

    def links(self) -> List[str]:
        request_options = self._create_request_options()

        # This function should be defined or imported in your code
        result = get_urls(request_options, self.urls)

        all_urls = []
        for x in result:
            all_urls.extend(x)

        # This function should be defined or imported in your code
        result = apply_filters_maps_sorts_randomize(
            request_options,
            all_urls,
            self.filters,
            self.extractors,
            self.sort_links,
            self.randomize_links,
        )

        return result

    def sitemaps(self) -> List[str]:
        request_options = self._create_request_options()

        # This function should be defined or imported in your code
        result = get_sitemaps_urls(request_options, self.urls)

        all_urls = []
        for x in result:
            all_urls.extend(x)

        # This function should be defined or imported in your code
        result = apply_filters_maps_sorts_randomize(
            request_options,
            all_urls,
            self.filters,
            self.extractors,
            self.sort_links,
            self.randomize_links,
        )

        return result

    def _create_request_options(self):
        return {
            **default_request_options,
            "parallel": 40,
            "cache": self.cache,
        }
