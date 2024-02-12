from core.tg.bot_dispatcher import BotDispatcher
from db import db

if __name__ == '__main__':
    bot_dispatcher = BotDispatcher(db)
    bot_dispatcher.start_polling()
