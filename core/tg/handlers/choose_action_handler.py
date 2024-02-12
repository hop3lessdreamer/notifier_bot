from aiogram.types import CallbackQuery

from core.tg.handlers.base_handler import BaseHandler
from core.tg.keyboards import MenuKeyboard
from core.tg.message_texts import Messages as Msg


class ChooseActionHandler(BaseHandler):
    def register_handlers(self):
        self.dp.register_callback_query_handler(self.choose_wb_actions, text='wildberries')

    @staticmethod
    async def choose_wb_actions(call: CallbackQuery):
        await call.message.edit_text(Msg.CHOSE_ACTION, reply_markup=MenuKeyboard())
        await call.answer()
