import logging.handlers
import tornado.template
import os
from tornado.options import define, options

import environment
import logconfig


# Make filepaths relative to settings.
def path(root, *paths):
    return os.path.join(root, *paths)


ROOT = os.path.dirname(os.path.abspath(__file__))

define("port", default=8888, help="run on the given port", type=int)
define("host", default='localhost', help="run on the given host", type=str)
define("config", default=None, help="tornado config file")
define("debug", default=False, help="debug mode")
tornado.options.parse_command_line()

MEDIA_ROOT = path(ROOT, 'media')
TEMPLATE_ROOT = path(ROOT, 'templates')


# Deployment Configuration

class DeploymentType:
    PRODUCTION = "PRODUCTION"
    DEV = "DEV"
    SOLO = "SOLO"
    STAGING = "STAGING"
    TEST = "TEST"
    dict = {
        SOLO: 1,
        PRODUCTION: 2,
        DEV: 3,
        STAGING: 4,
        TEST: 5
    }


if 'DEPLOYMENT_TYPE' in os.environ:
    DEPLOYMENT = os.environ['DEPLOYMENT_TYPE'].upper()
else:
    DEPLOYMENT = DeploymentType.SOLO


secret_tokens = {
    'cookie_secret': "your-cookie-secret",
    'password_pepper': "your-password-pepper"
}

tornado_settings = {
    'debug': (DEPLOYMENT != DeploymentType.PRODUCTION
              and DEPLOYMENT != DeploymentType.TEST) or options.debug,
    'static_path': MEDIA_ROOT,
    'cookie_secret': secret_tokens['cookie_secret'],
    'xsrf_cookies': True,
}

db_settings = {
    'engine': 'tortoise.backends.mysql',
    'credentials': {
        'host': "localhost",
        'port': 3306,
        'user': "whitelist",
        'password': "TzlKJNm980kArQCpsHmeBhoha9qLGRn6",
        'database': "whitelist",
        'echo': tornado_settings['debug']
    }
}

SYSLOG_TAG = "whitelist"
SYSLOG_FACILITY = logging.handlers.SysLogHandler.LOG_LOCAL2

# See PEP 391 and logconfig for formatting help.  Each section of LOGGERS
# will get merged into the corresponding section of log_settings.py.
# Handlers and log levels are set up automatically based on LOG_LEVEL and DEBUG
# unless you set them here.  Messages will not propagate through a logger
# unless propagate: True is set.
LOGGERS = {
   'loggers': {
       'whitelist': {},
       'db_client': {},
       'aiosqlite': {}
   },
}

if tornado_settings['debug']:
    LOG_LEVEL = logging.DEBUG
else:
    LOG_LEVEL = logging.INFO
USE_SYSLOG = DEPLOYMENT != DeploymentType.SOLO

logconfig.initialize_logging(SYSLOG_TAG, SYSLOG_FACILITY, LOGGERS,
                             LOG_LEVEL, USE_SYSLOG)

if options.config:
    tornado.options.parse_config_file(options.config)
