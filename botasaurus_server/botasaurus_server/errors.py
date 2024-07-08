import json
from bottle import HTTPResponse


def add_cors_headers(headers):
        headers['Access-Control-Allow-Origin'] = '*'
        headers['Access-Control-Allow-Methods'] = \
            'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        headers['Access-Control-Allow-Headers'] = \
            'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
        return headers

def add_cors_headers_download(headers):
        headers['Access-Control-Allow-Origin'] = '*'
        headers['Access-Control-Allow-Methods'] = \
            'GET, POST, PUT, OPTIONS'
        headers['Access-Control-Allow-Headers'] = \
            'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'
        headers["Access-Control-Expose-Headers"] = "Content-Disposition"
        return headers
class DownloadResponse(HTTPResponse):
    def __init__(self, body=None, status=None, headers=None,):
        headers = add_cors_headers_download(headers or {})
        super().__init__(body, status, headers,)

class JsonHTTPResponse(HTTPResponse):
    def __init__(self, body=None, status=400, headers=None, **more_headers):
        headers = add_cors_headers(headers or {})
        headers.update({"Content-Type": "application/json"})

        if body is not None and not isinstance(body, str):
            body = json.dumps(body)

        super().__init__(body, status, headers, **more_headers)


class JsonHTTPResponseWithMessage(HTTPResponse):
    def __init__(self, body=None, status=400, headers=None, **more_headers):
        headers = add_cors_headers(headers or {})
        headers.update({"Content-Type": "application/json"})

        body = json.dumps({"message":body})

        super().__init__(body, status, headers, **more_headers)
