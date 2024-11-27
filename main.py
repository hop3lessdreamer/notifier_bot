import asyncio

from core.tg.bot import bot
from core.tg.bot_dispatcher import BotDispatcher
from core.tg.tg_dispatcher import tg_disp
from db import db


async def main() -> None:
    await BotDispatcher(db, bot, tg_disp).start_polling()


if __name__ == '__main__':
    #   check cd
    asyncio.run(main())
