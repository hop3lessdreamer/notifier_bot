from asyncio import get_event_loop

from aiogram import Dispatcher

from core.tg.storage import Storage


class TgDispatcher(Dispatcher):
    def __init__(self) -> None:
        super().__init__(
            loop=get_event_loop(),
            storage=Storage(),
            run_tasks_by_default=False,
            no_throttle_error=False,
            filters_factory=None,
        )


tg_disp = TgDispatcher()
