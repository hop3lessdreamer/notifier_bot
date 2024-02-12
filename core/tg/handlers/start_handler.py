""""""

from aiogram.types import Message, InlineKeyboardMarkup

from core.tg.buttons import AVAILABLE_MARKET_PLACES
from core.tg.handlers.base_handler import BaseHandler
from core.tg.message_texts import Messages as Msg


class StartHandler(BaseHandler):
    def register_handlers(self):
        self.dp.register_message_handler(self.start_message, commands='start')

    async def start_message(self, message: Message):
        """"""

        await message.answer(Msg.HELLO)

        user_id: int = message.from_user.id
        await self.db.create_user(user_id)

        keyboard = InlineKeyboardMarkup()
        keyboard.add(*AVAILABLE_MARKET_PLACES)

        await message.answer(Msg.CHOSE_MARKET_PLACE, reply_markup=keyboard)
