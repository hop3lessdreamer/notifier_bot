import asyncio

from core.tg.bot import bot
from core.tg.bot_dispatcher import BotDispatcher
from core.tg.tg_dispatcher import tg_disp
from db import db
from logger import init_logger


async def main() -> None:
    await BotDispatcher(db, bot, tg_disp).start_polling()


if __name__ == '__main__':
    init_logger()
    asyncio.run(main())
