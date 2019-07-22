import json
import logging
import tornado.web
import time
import traceback
from typing import Any, Optional

from logconfig import log_request
from handlers.utils import APIMissingParams, APIBadRequest, APIError,\
    get_session_user
from orm.models import User


logger = logging.getLogger('whitelist.' + __name__)


class BaseHandler(tornado.web.RequestHandler):
    """A class to collect common handler methods - all other handlers should
    subclass this one.
    """
    begin_time: int = None

    def load_json(self):
        """Load JSON from the request body and store them in
        self.request.arguments, like Tornado does by default for POSTed form
        parameters.

        If JSON cannot be decoded, raises an HTTPError with status 400.
        """
        try:
            self.request.arguments = json.loads(self.request.body)
        except ValueError:
            msg = f"Could not decode JSON: {self.request.body}"
            logger.debug(msg)
            raise APIBadRequest(msg)

    def get_current_user(self) -> Optional[User]:
        return get_session_user(self)

    def get_json_argument(self, name, default=None):
        """Find and return the argument with key 'name' from JSON request data.
        Similar to Tornado's get_argument() method.
        """
        if default is None:
            default = tornado.web._ARG_DEFAULT
        if not self.request.arguments:
            self.load_json()
        if name not in self.request.arguments:
            if default is tornado.web._ARG_DEFAULT:
                msg = f"Missing argument '{name}'"
                logger.debug(msg)
                raise APIMissingParams(msg)
            logger.debug(f"Returning default argument {default}, as we "
                         f"couldn't find '{name}' in {self.request.arguments}")
            return default
        arg = self.request.arguments[name]
        logger.debug(f"Found '{name}': {arg} in JSON arguments")
        if isinstance(arg, list):
            arg = arg[-1].decode()
        return arg

    def write_error(self, status_code: int, **kwargs: Any):
        if 'exc_info' in kwargs:
            logger.error(f"Exception caught:\n{traceback.format_exc()}")
            send_traceback = self.settings.get('serve_traceback', False) and\
                             'json' not in self.request.headers.get('Accept', '')
            if send_traceback:
                self.set_header('Content-Type', "text/plain")
                for line in traceback.format_exception(*kwargs['exc_info']):
                    self.write(line)
                self.write("\nResponse body:\n")
            exception = kwargs['exc_info'][1]
            if isinstance(exception, APIError):
                if not send_traceback:
                    self.set_header('Content-Type', "application/json")
                self.write(exception.log_message)
            self.finish()
        else:
            self.finish("<html><title>{code}: {message}</title>"
                        "<body>{code}: {message}</body></html>".format(
                            code=status_code, message=self._reason))

    def prepare(self):
        _ = self.xsrf_token  # force set xsrf token
        self.begin_time = int(time.time() * 1000)

    def on_finish(self):
        log_request(self.request, int(time.time() * 1000) - self.begin_time,
                    self._status_code)
