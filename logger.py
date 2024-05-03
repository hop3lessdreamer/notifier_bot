""" Initiation logger """
from typing import Any, get_type_hints

from loguru import logger as loguru_logger

from config import bot_config


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
        enqueue=True,
        diagnose=True,
        rotation='10 MB',
    )
    return loguru_logger


get_type_hints(create_logger)
#   variable for import in other modules to logging
logger = create_logger()
logger.info(f'init logger (path={bot_config.LOG_PATH}, level={bot_config.LOG_LEVEL})')
