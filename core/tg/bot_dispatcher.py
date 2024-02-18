from asyncio import get_event_loop, sleep
from dataclasses import dataclass

from aiogram import Bot, Dispatcher
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.types import ParseMode
from aiogram.utils import executor

# from aiogram.utils.executor import start_webhook
from config import bot_config
from core.tg.handlers import HANDLERS
from core.tg.storage import Storage

# from core.wb.utils import check_product_prices
from db import Database
from db.queries import DBQueries
from logger import loguru_logger

# async def on_startup(dp: TGDispatcher) -> None:
#     await dp.bot.set_webhook(
#         url=bot_config.webhook_url,
#         drop_pending_updates=True
#     )
#
#
# async def on_shutdown(dp: TGDispatcher) -> None:
#     await dp.bot.delete_webhook()


@dataclass
class BotDispatcher:
    db: Database
    dp: Dispatcher = Dispatcher(
        Bot(bot_config.API_TOKEN, parse_mode=ParseMode.HTML),
        loop=get_event_loop(),
        storage=Storage(),
        run_tasks_by_default=False,
        throttling_rate_limit=DEFAULT_RATE_LIMIT,
        no_throttle_error=False,
        filters_factory=None,
    )

    async def __check_product_prices_task(self) -> None:
        """"""

        while True:
            await sleep(bot_config.PRICE_CHECKS_FREQUENCY)
            # await check_product_prices(DBQueries(self.db), self.dp)

    async def register_handlers(self) -> None:
        for handler in HANDLERS:
            db: DBQueries = DBQueries(self.db)
            handler(db, self.dp).register_handlers()

    def start_polling(self) -> None:
        """"""

        # start_webhook(
        #     dispatcher=self.dp,
        #     webhook_path=bot_config.WEBHOOK_PATH,
        #     skip_updates=True,
        #     on_startup=on_startup,
        #     on_shutdown=on_shutdown,
        #     host=bot_config.WEBAPP_HOST,
        #     port=bot_config.WEBAPP_PORT
        # )
        loguru_logger.info('start bot')
        self.dp.loop.create_task(self.register_handlers())
        self.dp.loop.create_task(self.__check_product_prices_task())

        executor.start_polling(self.dp, skip_updates=True)
