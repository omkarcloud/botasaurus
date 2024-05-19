import json
from bottle import HTTPResponse

class JsonHTTPResponse(HTTPResponse):
    def __init__(self, body=None, status=400, headers=None, **more_headers):
        headers = headers or {}
        headers.update({"Content-Type": "application/json"})

        if body is not None and not isinstance(body, str):
            body = json.dumps(body)

        super().__init__(body, status, headers, **more_headers)


class JsonHTTPResponseWithMessage(HTTPResponse):
    def __init__(self, body=None, status=400, headers=None, **more_headers):
        headers = headers or {}
        headers.update({"Content-Type": "application/json"})

        body = json.dumps({"message":body})

        super().__init__(body, status, headers, **more_headers)
