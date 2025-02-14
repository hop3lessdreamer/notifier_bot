""" Initiation logger """
import functools
import sys
from collections.abc import Callable
from typing import Any

from loguru import logger

from config import bot_config

LOG_FORMAT = '>>> {time: DD.MM.YY HH:mm:ss.SS} | {level} | {function} | {message}'


def init_logger() -> None:
    """Create and return Logger"""
    logger.remove()
    if not bot_config.LOG_PATH:
        logger.add(sys.stdout, level='DEBUG')
        return

    logger.add(
        bot_config.LOG_PATH,
        level=bot_config.LOG_LEVEL or 'DEBUG',
        format=LOG_FORMAT,
        enqueue=True,
        diagnose=True,
        rotation='10 MB',
    )
    logger.info(f'init logger (path={bot_config.LOG_PATH}, level={bot_config.LOG_LEVEL})')


def log_node(msg: str, level: str = 'INFO') -> Callable:
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            logger.log(level, f'[s_node]{msg}')
            result = await fn(*args, **kwargs)
            logger.log(level, '[f_node]')
            return result

        return wrapper

    return decorator
