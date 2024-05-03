from aiogram.types import CallbackQuery

from core.tg.handlers import BaseHandler
from core.tg.keyboards import ProductKeyboard
from core.tg.notifier_state import NotifierState
from core.tg.storage import Context


class OnNotifyHandler(BaseHandler):
    def register_handlers(self) -> None:
        self.dp.register_callback_query_handler(
            self.change_threshold_on_notify, text='change_threshold_on_notify'
        )

    @staticmethod
    async def change_threshold_on_notify(call: CallbackQuery, state: Context) -> None:
        await call.message.edit_reply_markup(reply_markup=ProductKeyboard())
        await state.set_state(NotifierState.waiting_action_w_product.state)
