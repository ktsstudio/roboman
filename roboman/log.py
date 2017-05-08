import logging
import os
import socket
from datetime import datetime


class LogFormatter(logging.Formatter):
    def __init__(self, **kwargs):
        super().__init__('{host} {timestamp} {time} {level} {pid} >>> {message}', None, '{')

    def format(self, record):
        now = datetime.now()

        record.host = socket.gethostname()
        record.time = now.strftime('%Y-%m-%dT%H:%M:%S.%f')
        record.timestamp = int(now.timestamp())
        record.level = record.levelname[0]
        record.pid = os.getpid()

        return super().format(record)


loggers = dict()


def get_logger(name, level=None):
    if name not in loggers:
        logger = logging.getLogger(name)

        handler_console = logging.StreamHandler()
        handler_console.setFormatter(LogFormatter())

        logger.addHandler(handler_console)
        logger.setLevel(level or logging.INFO)

        loggers[name] = logger

    return loggers[name]
