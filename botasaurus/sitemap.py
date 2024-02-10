import xml.etree.ElementTree as ET
from urllib.parse import urlparse, unquote_plus
from gzip import decompress
from .decorators import request

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


def gunzip(data: bytes) -> bytes:
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
def fetch_content(request, url):
    """Fetch content from a URL, handling gzip if necessary."""
    response = request.get(url, timeout=30)
    status_code = response.status_code

    if status_code == 404:
        print("Sitemap not found (404) at the following URL: " + response.url)
        return None

    response.raise_for_status()

    if isgzip(url, response):
        return gunzip(response.content)
    else:
        return response.text


class Sitemap:
    def __init__(self, urls, cache=True):
        self.urls = urls if isinstance(urls, list) else [urls]
        self.cache = cache

    def links(self):
        all_urls = []
        visited = set()

        @request(**default_request_options, parallel=40, cache=self.cache)
        def sitemaps_json(req, url):
            """Recursively parse a sitemap, including nested sitemaps."""

            nonlocal visited  # Reference the global visited set

            # If the URL has already been visited, return an empty list to prevent infinite recursion
            if url in visited:
                return []

            visited.add(url)

            content = fetch_content(url)

            if not content:
                return []

            root = ET.fromstring(content)

            # Namespace handling, as sitemap XMLs often define namespaces
            namespaces = {"sitemap": "http://www.sitemaps.org/schemas/sitemap/0.9"}

            links = []
            # Look for URL entries, which indicate actual page links
            for url_entry in root.findall("sitemap:url", namespaces):
                loc = url_entry.find("sitemap:loc", namespaces).text
                links.append(loc)

            # Look for sitemap entries, which indicate nested sitemaps
            locs = [
                sitemap.find("sitemap:loc", namespaces).text
                for sitemap in root.findall("sitemap:sitemap", namespaces)
            ]

            parsed = sitemaps_json(locs)

            for x in parsed:
                links.extend(x)

            return links

        result = sitemaps_json(
            self.urls,
        )

        for x in result:
            all_urls.extend(x)

        # Uniqify the
        all_urls = list(dict.fromkeys(all_urls))

        return all_urls


if __name__ == "__main__":
    sitemap = Sitemap("https://www.g2.com/sitemaps/sitemap_index.xml.gz")
    print(sitemap.links())
