from asyncio import get_event_loop

from aiogram import Bot, Dispatcher
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.types import ParseMode

from config import bot_config
from core.tg.storage import Storage


class TgDispatcher(Dispatcher):
    def __init__(self) -> None:
        super().__init__(
            Bot(bot_config.API_TOKEN, parse_mode=ParseMode.HTML),
            loop=get_event_loop(),
            run_tasks_by_default=False,
            throttling_rate_limit=DEFAULT_RATE_LIMIT,
            no_throttle_error=False,
            filters_factory=None,
        )
        self.storage: Storage = Storage()
