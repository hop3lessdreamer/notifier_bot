from asyncio import sleep
from dataclasses import dataclass

from aiogram.utils import executor

from core.tg.handlers import HANDLERS
from core.tg.tg_dispatcher import TgDispatcher
from core.wb.utils import check_product_prices
from db import Database
from db.queries import DBQueries
from logger import logger


@dataclass
class BotDispatcher:
    db: Database
    dp: TgDispatcher = TgDispatcher()

    async def __check_product_prices_task(self) -> None:
        """"""

        while True:
            await sleep(20)
            await check_product_prices(DBQueries(self.db), self.dp)

    async def register_handlers(self) -> None:
        for handler in HANDLERS:
            db: DBQueries = DBQueries(self.db)
            handler(db, self.dp).register_handlers()

    def start_polling(self) -> None:
        """"""

        logger.info('start bot')
        self.dp.loop.create_task(self.register_handlers())
        self.dp.loop.create_task(self.__check_product_prices_task())

        executor.start_polling(self.dp, skip_updates=True)
