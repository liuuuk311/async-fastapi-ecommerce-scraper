import logging
import sys

from web.core.config import settings


def get_logger(_name):
    _logger = logging.getLogger(_name)
    log_format = '%(asctime)s - %(levelname)s: %(message)s'
    logging.basicConfig(format=log_format)

    _logger.setLevel(settings.LOG_LEVEL)

    return _logger
