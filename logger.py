""" Initiation logger """
import functools
from collections.abc import Callable
from typing import Any, get_type_hints

from loguru import logger as loguru_logger

from config import bot_config

LOG_FORMAT = '>>>{time: DD.MM.YY HH:mm:ss.SS} | {level} | {function} | {message}'


class MockLogger:
    def info(self, __message: str, *args: Any, **kwargs: Any) -> None:
        ...

    def warning(self, __message: str, *args: Any, **kwargs: Any) -> None:
        ...

    def error(self, __message: str, *args: Any, **kwargs: Any) -> None:
        ...

    def catch(self, *args: Any, **kwargs: Any) -> None:
        ...


def create_logger() -> loguru_logger:  # type: ignore
    """Create and return Logger"""

    if not bot_config.LOG_PATH or not bot_config.LOG_LEVEL:
        return MockLogger()

    loguru_logger.add(
        bot_config.LOG_PATH,
        level=bot_config.LOG_LEVEL,
        format=LOG_FORMAT,
        enqueue=True,
        diagnose=True,
        rotation='10 MB',
    )
    return loguru_logger


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


get_type_hints(create_logger)
#   variable for import in other modules to logging
logger = create_logger()
logger.info(f'init logger (path={bot_config.LOG_PATH}, level={bot_config.LOG_LEVEL})')
