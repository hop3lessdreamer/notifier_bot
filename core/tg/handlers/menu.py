from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from core.tg.handlers import BaseHandler
from core.tg.keyboards import MenuKeyboard, MenuKeyboardWEmptySubs
from core.tg.notifier_state import NotifierState
from core.tg.message_texts import Messages as Msg


class PickMenu(BaseHandler):
    def register_handlers(self):
        self.dp.register_callback_query_handler(
            self.menu,
            text='menu',
            state=NotifierState.waiting_action_w_product_for_exist.state
        )
        self.dp.register_callback_query_handler(
            self.menu_from_choosing_product,
            text='menu',
            state=NotifierState.waiting_product_id.state
        )
        self.dp.register_callback_query_handler(
            self.menu_from_choosing_product,
            text='menu',
            state=NotifierState.waiting_product_id_for_del_subscribe.state
        )
        self.dp.register_message_handler(
            self.menu_command,
            commands='menu'
        )

    @staticmethod
    async def menu(call: CallbackQuery, state: FSMContext):
        await call.message.edit_reply_markup(reply_markup=MenuKeyboard())
        await state.finish()

    async def menu_command(self, message: Message, state: FSMContext):
        subs_cnt: int = await self.db.get_cnt_subscription_by_user(state.user)
        if not subs_cnt:
            await message.answer(Msg.CHOSE_ACTION, reply_markup=MenuKeyboardWEmptySubs())
            return

        await message.answer(Msg.CHOSE_ACTION, reply_markup=MenuKeyboard())

    @staticmethod
    async def menu_from_choosing_product(call: CallbackQuery, state: FSMContext):
        await call.message.edit_text(Msg.CHOSE_ACTION, reply_markup=MenuKeyboard())
        await state.finish()
