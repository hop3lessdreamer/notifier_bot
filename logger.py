""" Initiation logger """

from loguru import logger as loguru_logger
from typing import get_type_hints

from config import bot_config


def create_logger() -> loguru_logger:
    """ Create and return Logger """
    loguru_logger.add(bot_config.LOG_PATH, level=bot_config.LOG_LEVEL)
    return loguru_logger.bind()


get_type_hints(create_logger)
#   variable for import in other modules to logging
logger = create_logger()
