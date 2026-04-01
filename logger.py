"""Logging setup — configures the shared 'image_server' logger."""

import logging
import os

from config import LOGS_DIR, LOG_LEVEL, LOG_FILE, LOG_FORMAT, LOG_DATE_FORMAT

os.makedirs(LOGS_DIR, exist_ok=True)


def setup_logger():
    logger = logging.getLogger('image_server')
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    if logger.handlers:
        return logger

    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    file_handler = logging.FileHandler(
        os.path.join(LOGS_DIR, LOG_FILE), encoding='utf-8'
    )
    file_handler.setLevel(logger.level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logger.level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
