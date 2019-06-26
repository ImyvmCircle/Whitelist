import tornado.httputil
import logging


logger = logging.getLogger('whitelist.' + __name__)


def log_request(request: tornado.httputil.HTTPServerRequest, time: int,
                status: int):
    logger.info(f"{request.remote_ip} {request.method} {request.path} "
                f"{request.host} {status} {time}")
