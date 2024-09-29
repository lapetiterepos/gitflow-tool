import logging
import settings.config as config

_log_format = "%(color)s%(asctime)s : %(levelname)s : <%(filename)s:%(funcName)s:%(lineno)d> : %(message)s"
_time_format = "%Y-%m-%dT%H:%M:%S%z"


class CustomFilter(logging.Filter):

    COLOR = {
        "DEBUG": "\x1b[38;21m",
        "INFO": "\x1b[38;21m",
        "WARNING": "\x1b[38;5;226m",
        "ERROR": "\x1b[31;1m",
        "CRITICAL": "\x1b[38;5;196m",
    }

    def filter(self, record):
        record.color = CustomFilter.COLOR[record.levelname]
        return True


class UrlAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        url = kwargs.pop("url", self.extra["url"])
        if not url:
            return "%s" % msg, kwargs
        return "%s : %s" % (msg, url), kwargs


def get_logger(name):
    logger = logging.getLogger(name)
    numeric_level = getattr(logging, config.logger.level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {config.logger.level}")
    logger.setLevel(numeric_level)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(fmt=_log_format, datefmt=_time_format)
    logger.addFilter(CustomFilter())
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger = UrlAdapter(logger, {"url": None})
    return logger
