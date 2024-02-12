from asyncio import get_event_loop, sleep
from dataclasses import dataclass

from aiogram import Bot, Dispatcher, executor
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.types import ParseMode

from config import bot_config
from core.tg.handlers import HANDLERS
from core.tg.storage import Storage
from db import Database
from db.queries import DBQueries
from logger import loguru_logger


class TGDispatcher(Dispatcher):
    def __init__(self) -> None:
        super().__init__(
            Bot(bot_config.API_TOKEN, parse_mode=ParseMode.HTML),
            loop=get_event_loop(),
            storage=Storage(),
            run_tasks_by_default=False,
            throttling_rate_limit=DEFAULT_RATE_LIMIT,
            no_throttle_error=False,
            filters_factory=None,
        )


@dataclass
class BotDispatcher:
    db: Database
    dp: TGDispatcher = TGDispatcher()

    @staticmethod
    async def __check_product_prices_task() -> None:
        """"""

        while True:
            await sleep(bot_config.PRICE_CHECKS_FREQUENCY)
            print("CHECK PRICES")

    async def register_handlers(self) -> None:
        for handler in HANDLERS:
            db: DBQueries = DBQueries(self.db)
            handler(db, self.dp).register_handlers()

    def start_polling(self) -> None:
        """"""
        loguru_logger.info('start bot')
        self.dp.loop.create_task(self.register_handlers())
        self.dp.loop.create_task(self.__check_product_prices_task())

        executor.start_polling(self.dp, skip_updates=True)
