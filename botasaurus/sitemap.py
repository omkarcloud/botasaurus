import re
from urllib.parse import urlparse, unquote_plus, urlunparse
from gzip import decompress
from typing import List
from bs4 import BeautifulSoup
import traceback
# Import Filters, Extractors are imported from Sitemaps
from .links import _Base,Filters, Extractors, apply_filters_maps_sorts_randomize, extract_link_upto_nth_segment
from botasaurus.dontcache import is_dont_cache
from .cache import DontCache
from .list_utils import flatten
from .cl import join_link
from .request_decorator import request
from .output import write_json

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
def handle_response(url, response):
    if response.status_code == 404:
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

@request(
    **default_request_options,
)
def fetch_content(request, url: str):
    """Fetch content from a URL, handling gzip if necessary."""
    try:
        response = request.get(url, timeout=60)
        return handle_response(url, response)

    except Exception as e:
        print(f"failed for {url} due to {str(e)}. Retrying")

        try:
            response = request.get(url, timeout=60)
            
            result =  handle_response(url, response)
            if result is not None:
                print(f"succeeded for {url}")
            return result
        except Exception as e:
            print(f"skipping {url} as it failed after retry")
            traceback.print_exc()

        return None

def wrap_in_sitemap(urls):
    return [{"url":url, "type":"sitemap"} for url in urls]

def clean_sitemap_response(s, char='<'):
    # Find the index of the given character
    if not s:
        return s
    
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
            return DontCache([])

        locs = find_the_sitemaps(content)

        links = [url]

        parsed = sitemap(wrap_in_sitemap(locs), return_dont_cache_as_is=True)

        isdn_cache = False
        for x in parsed:
            if is_dont_cache(x):
                isdn_cache = True
                links.extend(x.data)
            else:
                links.extend(x)

        if isdn_cache:
            return DontCache(links)

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
            return DontCache([])

        links, locs = get_links_sitemaps(content)

        parsed = sitemap(locs, return_dont_cache_as_is=True)

        isdn_cache = False
        for x in parsed:
            if is_dont_cache(x):
                isdn_cache = True
                links.extend(x.data)
            else:
                links.extend(x)

        if isdn_cache:
            return DontCache(links)

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
            return DontCache([])

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


class Sitemap(_Base):
    def __init__(self, urls, cache=True):
        self.cache = cache
        self.filters = []  # Existing filters list
        self.extractors = []  # New list for extractors
        self.sort_links = False  # Flag for sorting links
        self.randomize_links = False  # Flag for randomizing links

        urls = urls if isinstance(urls, list) else [urls]

        urls = get_sitemaps_from_robots(self._create_request_options(), urls )
        self.urls = urls

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

    def write_links(self, filename: str):
        results = self.links()
        write_json(results, filename)
        return results
    
    def write_sitemaps(self, filename: str):
        results = self.sitemaps()
        write_json(results, filename)
        return results
    
    def _create_request_options(self):
        return {
            **default_request_options,
            "parallel": 40,
            "cache": self.cache,
        }

