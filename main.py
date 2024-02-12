from core.tg.bot_dispatcher import BotDispatcher
from db import db

if __name__ == '__main__':
    bot_dispatcher = BotDispatcher(db)
    bot_dispatcher.start_polling()

    # from core.wb.wb_parser import WbParser
    # from logger import logger
    # logger.info('check!')
    # async def t():
    #     wb_parser = await WbParser([61938863, 115779302, 23]).get_wb_products()
    #     print(wb_parser)
    #
    # import asyncio
    # asyncio.run(t())
