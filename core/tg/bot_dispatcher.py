from dataclasses import dataclass

from aiogram import Bot

from core.tg.handlers import get_main_router
from core.tg.middlewares.services import ServicesMiddleware
from core.tg.tg_dispatcher import TgDispatcher
from db import Database
from logger import logger as loguru_logger


@dataclass
class BotDispatcher:
    db: Database
    bot: Bot
    dp: TgDispatcher

    async def start_polling(self) -> None:
        loguru_logger.info('start polling...')
        self.dp.update.outer_middleware(ServicesMiddleware(self.db))
        self.dp.include_router(get_main_router())
        await self.dp.start_polling(self.bot)
