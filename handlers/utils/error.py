import json
from tornado.web import HTTPError


class APIError(HTTPError):
    def __init__(self, error_type="", status=500, message: str = None,
                 *args, **kwargs):
        text = {
            'error': error_type,
            'message': message
        }
        text = json.dumps(text)
        super(APIError, self).__init__(status, text, *args, **kwargs)


class APIBadRequest(APIError):
    def __init__(self, message="Bad request", *args, **kwargs):
        super(APIBadRequest, self)\
            .__init__("value:bad_request", 400, message, *args, **kwargs)


class APIValueError(APIError):
    def __init__(self, message="Value is invalid", *args, **kwargs):
        super(APIValueError, self)\
            .__init__("value:invalid", 400, message, *args, **kwargs)


class APIMissingParams(APIError):
    def __init__(self, message="Some parameter are missing", *args, **kwargs):
        super(APIMissingParams, self)\
            .__init__("value:missing_params", 400, message, *args, **kwargs)


class APINotFoundError(APIError):
    def __init__(self, message="Resource not found", *args, **kwargs):
        super(APINotFoundError, self)\
            .__init__("value:not_found", 404, message, *args, **kwargs)


class APIPermissionError(APIError):
    def __init__(self, message="Access denied", *args, **kwargs):
        super(APIPermissionError, self)\
            .__init__("permission:forbidden", 403, message, *args, **kwargs)


class APILoginNeeded(APIError):
    def __init__(self, message="Login needed", *args, **kwargs):
        super(APILoginNeeded, self)\
            .__init__("permission:login_needed", 401, message, *args, **kwargs)
