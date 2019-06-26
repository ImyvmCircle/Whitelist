#!/usr/bin/env python3

import asyncio
import logging
import tornado.httpserver
import tornado.httputil
import tornado.ioloop
import tornado.autoreload
import tornado.web
from tornado.options import options

from settings import tornado_settings
from urls import url_patterns
import orm


logger = logging.getLogger('whitelist.' + __name__)


class TornadoWeb(tornado.web.Application):
    def __init__(self):
        super(TornadoWeb, self).__init__(url_patterns, **tornado_settings)


def main():
    tornado.autoreload.add_reload_hook(
        lambda: logger.info('Server is being reloaded'))
    app = TornadoWeb()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port, options.host)
    logger.info(f"Server is listening on http://{options.host}:{options.port}")
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(orm.init())
        main()
    except KeyboardInterrupt:
        logger.info('Keyboard interrupt received, quiting...')
    finally:
        loop.run_until_complete(orm.close())
