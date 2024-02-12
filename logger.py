""" Initiation logger """

from typing import get_type_hints

from loguru import logger as loguru_logger

from config import bot_config


def create_logger() -> loguru_logger:
    """ Create and return Logger """
    loguru_logger.add(
        bot_config.LOG_PATH,
        level=bot_config.LOG_LEVEL,
        enqueue=True,
        diagnose=True,
        rotation='10 MB'
    )
    return loguru_logger


get_type_hints(create_logger)
#   variable for import in other modules to logging
logger = create_logger()
