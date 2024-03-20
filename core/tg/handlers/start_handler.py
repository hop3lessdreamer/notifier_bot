from aiogram.types import InlineKeyboardMarkup, Message

from core.tg.buttons import AVAILABLE_MARKET_PLACES
from core.tg.handlers.base_handler import BaseHandler
from core.tg.message_texts import Messages as Msg


class StartHandler(BaseHandler):
    def register_handlers(self) -> None:
        self.dp.register_message_handler(self.start_message, commands='start')

    async def start_message(self, message: Message) -> None:
        await message.answer(Msg.HELLO)

        await self.db.create_user(message.from_user.id, message.chat.id)

        keyboard = InlineKeyboardMarkup()
        keyboard.add(*AVAILABLE_MARKET_PLACES)

        await message.answer(Msg.CHOSE_MARKET_PLACE, reply_markup=keyboard)
