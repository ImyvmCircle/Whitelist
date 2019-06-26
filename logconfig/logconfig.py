"""An extended version of the log_settings module from zamboni:
https://github.com/jbalogh/zamboni/blob/master/log_settings.py
"""
from tornado.log import LogFormatter as TornadoLogFormatter
import logging
import logging.config
import logging.handlers
import os.path


# Pulled from commonware.log we don't have to import that, which drags with
# it Django dependencies.
class RemoteAddressFormatter(logging.Formatter):
    """Formatter that makes sure REMOTE_ADDR is available."""

    def format(self, record):
        if ('%(REMOTE_ADDR)' in self._fmt
                and 'REMOTE_ADDR' not in record.__dict__):
            record.__dict__['REMOTE_ADDR'] = None
        return logging.Formatter.format(self, record)


class UTF8SafeFormatter(RemoteAddressFormatter):
    def __init__(self, fmt=None, datefmt=None, encoding='utf-8'):
        logging.Formatter.__init__(self, fmt, datefmt)
        self.encoding = encoding

    def formatException(self, e):
        r = logging.Formatter.formatException(self, e)
        if isinstance(r, bytes):
            r = r.decode(self.encoding, 'replace')  # Convert to unicode
        return r

    def format(self, record):
        t = RemoteAddressFormatter.format(self, record)
        if isinstance(t, bytes):
            t = t.decode(self.encoding, 'replace')
        return t


class NullHandler(logging.Handler):
    def emit(self, record):
        pass


def initialize_logging(syslog_tag, syslog_facility, loggers,
                       log_level=logging.INFO, use_syslog=False):
    if os.path.exists('/dev/log'):
        syslog_device = '/dev/log'
    elif os.path.exists('/var/run/syslog'):
        syslog_device = '/var/run/syslog'
    else:
        syslog_device = '/dev/null'

    base_fmt = '%(name)s:%(levelname)s %(message)s:%(pathname)s:%(lineno)s'

    config = {
        'version': 1,
        'filters': {},
        'formatters': {
            'debug': {
                '()': UTF8SafeFormatter,
                'datefmt': '%H:%M:%s',
                'format': '%(asctime)s ' + base_fmt
            },
            'prod': {
                '()': UTF8SafeFormatter,
                'datefmt': '%H:%M:%s',
                'format': f'{syslog_tag}: [%(REMOTE_ADDR)s] {base_fmt}'
            },
            'tornado': {
                '()': TornadoLogFormatter,
                'color': True
            }
        },
        'handlers': {
            'console': {
                '()': logging.StreamHandler,
                'formatter': 'tornado'
            },
            'null': {
                '()': NullHandler
            },
            'syslog': {
                '()': logging.handlers.SysLogHandler,
                'facility': syslog_facility,
                'address': syslog_device,
                'formatter': 'prod'
            }
        },
        'loggers': {
        }
    }

    for key, value in loggers.items():
        config[key].update(value)

    # Set the level and handlers for all loggers.
    for logger in config['loggers'].values():
        if 'handlers' not in logger:
            logger['handlers'] = ['syslog' if use_syslog else 'console']
        if 'level' not in logger:
            logger['level'] = log_level
        if 'propagate' not in logger:
            logger['propagate'] = False

    logging.config.dictConfig(config)