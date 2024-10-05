from typing import List
import traceback
# Import Filters, Extractors are imported from Sitemaps
from .links import _Base,Filters, Extractors, apply_filters_maps_sorts_randomize, extract_link_upto_nth_segment
from botasaurus.dontcache import is_dont_cache
from .cache import DontCache
from .list_utils import flatten
from .request_decorator import request
from .output import write_json
from .sitemap_parser_utils import clean_robots_txt_url, fix_bad_sitemap_response, clean_sitemap_url, extract_sitemaps, split_into_links_and_sitemaps, fix_gzip_response, is_empty_path, parse_sitemaps_from_robots_txt, wrap_in_sitemap

default_request_options = {
    # "use_stealth": True,
    "raise_exception": True,
    "create_error_logs": False,
    "close_on_crash": True,
    "output": None,
}

@request(
    **default_request_options,
)
def fetch_content(request, url: str):
    """Fetch content from a URL, handling gzip if necessary."""
    try:
        response = request.get(url, timeout=60)
        return fix_gzip_response(url, response)

    except Exception as e:
        print(f"failed for {url} due to {str(e)}. Retrying")

        try:
            response = request.get(url, timeout=60)
            
            result =  fix_gzip_response(url, response)
            if result is not None:
                print(f"succeeded for {url}")
            return result
        except Exception as e:
            print(f"skipping {url} as it failed after retry")
            traceback.print_exc()

        return None

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

        content = fix_bad_sitemap_response(fetch_content(url,proxy = request_options['proxy']))
        if not content:
            return DontCache([])

        locs = extract_sitemaps(content)

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

        content = fix_bad_sitemap_response(fetch_content(url,proxy = request_options['proxy']))

        if not content:
            return DontCache([])

        links, locs = split_into_links_and_sitemaps(content)

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

    return sitemap(
        urls,
    )

def get_sitemaps_from_robots(request_options, urls):
    visited = set()

    @request(**request_options)
    def sitemap(req, url):

        nonlocal visited  # Reference the global visited set

        # If the URL has already been visited, return an empty list to prevent infinite recursion
        if url in visited:
            return []

        visited.add(url)
        content = fetch_content(url,proxy = request_options['proxy'])

        if not content:
            return DontCache([])

        result = parse_sitemaps_from_robots_txt(
            extract_link_upto_nth_segment(0, url), content
        )
        if not result:
            sm_url = clean_sitemap_url(url)
            content = fetch_content(sm_url,proxy = request_options['proxy'])
            if content:
                return [sm_url]
            return []

        return result
    ls = []
    
    for url in urls:
        temp = sitemap(clean_robots_txt_url(url)) if is_empty_path(url) else url
        ls.append(temp)
    
    return flatten(
      ls  
    )

class Sitemap(_Base):
    def __init__(self, urls, cache=True, proxy=None, parallel=40):
        self.cache = cache
        self.proxy = proxy
        self.parallel = parallel
        self._filters = []
        self._extractors = []
        self._sort_links = False
        self._randomize_links = False

        urls = urls if isinstance(urls, list) else [urls]

        urls = get_sitemaps_from_robots(self._create_request_options(), urls)
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
            self._filters,
            self._extractors,
            self._sort_links,
            self._randomize_links,
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
            self._filters,
            self._extractors,
            self._sort_links,
            self._randomize_links,
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
        options = {
            **default_request_options,
            "parallel": self.parallel,
            "cache": self.cache,
        }
        options["proxy"] = self.proxy
        return options