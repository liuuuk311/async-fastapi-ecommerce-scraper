import logging
import sys

from web.core.config import settings


def get_logger(_name):
    _logger = logging.getLogger(_name)

    stdout_handler = logging.StreamHandler(sys.stdout)
    # https://docs.python.org/3/library/logging.html#formatter-objects
    stdout_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    )
    _logger.addHandler(stdout_handler)
    _logger.setLevel(settings.LOG_LEVEL)

    return _logger
