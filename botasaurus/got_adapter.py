import os
from requests.cookies import RequestsCookieJar
from http.cookies import SimpleCookie
from requests.models import Response
from requests.auth import AuthBase, HTTPBasicAuth
from requests.utils import get_encoding_from_headers
from requests.structures import CaseInsensitiveDict


os.environ["timeout"] = "1000"
os.environ["TIMEOUT"] = "1000"

adapter = None
def get_adapter():
    global adapter
    if adapter:
      return adapter
    else:
      from javascript_fixes import require
      adapter = require("got-scraping-export")
      return adapter  
    
class GotAdapter:
    @staticmethod
    def _create_requests_cookie_jar_from_headers(response_headers):
        """
        Creates a RequestsCookieJar object from response headers.

        :param response_headers: A dictionary of response headers.
        :return: A RequestsCookieJar object containing the cookies.
        """
        cookie_jar = RequestsCookieJar()
        set_cookie_headers = response_headers.get("set-cookie")

        if set_cookie_headers:
            if isinstance(set_cookie_headers, str):
                set_cookie_headers = [set_cookie_headers]

            for item in set_cookie_headers:
                if item:
                    # Split the Set-Cookie header into individual cookie strings
                    # individual_cookies = item.split(',')

                    cookie = SimpleCookie()
                    cookie.load(item)

                    # # Process each cookie string
                    # for cookie_str in individual_cookies:
                    #     cookie = SimpleCookie()
                    #     cookie.load(cookie_str)

                    # Add each cookie to the RequestsCookieJar
                    for key, morsel in cookie.items():
                        cookie_jar.set(
                            key,
                            morsel.value,
                            domain=morsel["domain"],
                            path=morsel["path"],
                        )

        return cookie_jar

    @staticmethod
    def _convert_to_got_request(url, kwargs):
        headerGeneratorOptions = {
            "browsers": [{"name": "firefox", "minVersion": 114}],
            "devices": ["desktop"],
            "locales": ["en-US"],
            "operatingSystems": ["windows"],
        }
        # Map 'requests' arguments to 'got-scraping' arguments
        got_kwargs = {"url": url, "headerGeneratorOptions": headerGeneratorOptions}

        for key, value in kwargs.items():
            if key == "data":
                if value is not None:
                    if isinstance(value, dict):
                        raise ValueError("The 'data' parameter does not support dictionaries; use the 'json' parameter instead.")

                    got_kwargs["body"] = value
            elif key == "json":
                if value is not None:
                    got_kwargs["json"] = value
            elif key == "headers":
                dt = value or {}
                got_kwargs["headers"] = {**dt, **got_kwargs.get("headers", {})}
            elif key == "params":
                got_kwargs["searchParams"] = value
            elif key == "auth":
                if isinstance(value, tuple):
                    username, password = value
                elif isinstance(value, AuthBase) or isinstance(value, HTTPBasicAuth):
                    username, password = value.username, value.password
                else:
                    raise ValueError("Unsupported authentication type")

                got_kwargs["username"] = username
                got_kwargs["password"] = password
            elif key == "cookies":
                got_kwargs["headers"] = got_kwargs.get("headers", {})

                if "cookie" in got_kwargs["headers"]:
                    got_kwargs["headers"]["Cookie"] = got_kwargs["headers"]["cookie"]
                    del got_kwargs["headers"]["cookie"]

                cookie_header = "; ".join(
                    [str(x) + "=" + str(y) for x, y in value.items()]
                )

                if cookie_header:
                    if got_kwargs["headers"].get("Cookie"):
                        got_kwargs["headers"]["Cookie"] = (
                            got_kwargs["headers"]["Cookie"] + "; " + cookie_header
                        )
                    else:
                        got_kwargs["headers"]["Cookie"] = cookie_header

                    # or got_kwargs['headers']['cookie']:

                # if got_kwargs['headers']['cookie']:
                #     del got_kwargs['headers']['cookie']
            # elif key == 'files':
            #     got_kwargs['files'] = value  # May need special handling
            elif key == "timeout":
                got_kwargs["timeout"] = {"request": value * 1000}
            elif key == "proxies":
                if isinstance(value, dict):
                    value = value.get("http", value.get("https"))

                if value:
                    got_kwargs["proxyUrl"] = value
            elif key == "allow_redirects":
                got_kwargs["followRedirect"] = value
            elif key == "stream":
                raise ValueError("stream is not Supported")
                # got_kwargs['stream'] = value  # May need adjustment
            elif key == "verify":
                got_kwargs["https"] = {"rejectUnauthorized": value}
            elif key == "cert":
                raise ValueError("cert is not Supported")
            elif key == "files":
                raise ValueError("files is not Supported")
            elif key == "hooks":
                raise ValueError("hooks is not Supported")
            else:
                raise ValueError(f"{key} is not Supported")
            #
            # Add more conversions for other arguments as needed
        return got_kwargs

    @staticmethod
    def _convert_to_requests_response(gr):
        # return gr
        # return got_response
        response = Response()

        # Basic attributes
        response.status_code = gr.statusCode
        response.url = gr.url

        hd = {}
        for item in gr.headers:
            hd[item] = gr.headers[item]

        encoding = get_encoding_from_headers(hd)
        response.encoding = encoding
        response.headers = CaseInsensitiveDict(hd)
        response.reason = gr.statusMessage
        response.cookies = GotAdapter._create_requests_cookie_jar_from_headers(
            response.headers
        )

        if gr.body is not None:
            if encoding:
                response._content = gr.body.encode(encoding)
            else:
                response._content = gr.body.encode()

        return response

    @staticmethod
    def get(url, **kwargs):
        got_response = get_adapter().get(
            GotAdapter._convert_to_got_request(url, kwargs), timeout=300
        )
        return GotAdapter._convert_to_requests_response(got_response)

    @staticmethod
    def post(url, **kwargs):
        got_response = get_adapter().post(GotAdapter._convert_to_got_request(url, kwargs))
        return GotAdapter._convert_to_requests_response(got_response)

    @staticmethod
    def put(url, **kwargs):
        got_response = get_adapter().put(
            GotAdapter._convert_to_got_request(url, kwargs), timeout=300
        )
        return GotAdapter._convert_to_requests_response(got_response)

    @staticmethod
    def patch(url, **kwargs):
        got_response = get_adapter().patch(
            GotAdapter._convert_to_got_request(url, kwargs), timeout=300
        )
        return GotAdapter._convert_to_requests_response(got_response)

    @staticmethod
    def head(url, **kwargs):
        got_response = get_adapter().head(
            GotAdapter._convert_to_got_request(url, kwargs), timeout=300
        )
        return GotAdapter._convert_to_requests_response(got_response)

    @staticmethod
    def delete(url, **kwargs):
        got_response = get_adapter().delete(
            GotAdapter._convert_to_got_request(url, kwargs), timeout=300
        )
        return GotAdapter._convert_to_requests_response(got_response)


if __name__ == "__main__":
    # Initiate the web scraping task

    # gethttpbin()
    response = GotAdapter.get(
        "https://www.google.com/",
        headers={
            # "Referer": "https://www.google.com/",
        },
    )
    # print(response.json()['region'])
    # print(response._original_response.msg)
    # resp = requests.get('https://www.google.com/',  proxies=)
    print(response.reason)
    # print(response.content)
    # print(response)
    # print(response)
    # scrape_heading_task()
    # gethttpbin()
