from aiogram.types import InlineKeyboardMarkup, CallbackQuery

from core.tg.buttons import AVAILABLE_MARKET_PLACES
from core.tg.handlers import BaseHandler
from core.tg.message_texts import Messages as Msg


class ReChooseMP(BaseHandler):
    def register_handlers(self):
        self.dp.register_callback_query_handler(self.choose_mp, text='choose_marketplace')

    @staticmethod
    async def choose_mp(call: CallbackQuery):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(*AVAILABLE_MARKET_PLACES)
        await call.message.edit_text(Msg.CHOSE_MARKET_PLACE, reply_markup=keyboard)
