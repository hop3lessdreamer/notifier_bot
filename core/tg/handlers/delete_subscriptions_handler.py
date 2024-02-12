from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup

from core.tg.buttons import MENU_BTN
from core.tg.files import transferring_file
from core.tg.handlers.base_handler import BaseHandler
from core.tg.message_texts import Messages as Msg
from core.tg.notifier_state import NotifierState
from db.queries import Subscription

from utils.validators import validate_product_id


class DeleteSubscriptionHandlers(BaseHandler):
    def register_handlers(self):
        self.dp.register_callback_query_handler(self.delete_subscribe, text='delete_subscribe')
        self.dp.register_message_handler(
            self.delete_subscribe_for, state=NotifierState.waiting_product_id_for_del_subscribe.state
        )

    @staticmethod
    async def delete_subscribe(call: CallbackQuery, state: FSMContext):
        """"""
        keyboard = InlineKeyboardMarkup()
        keyboard.add(MENU_BTN)

        await state.set_state(NotifierState.waiting_product_id_for_del_subscribe.state)

        await call.message.answer(Msg.PRINT_PRODUCT, reply_markup=keyboard)
        await call.answer()

    async def delete_subscribe_for(self, message: Message, state: FSMContext):
        """"""

        user_msg: str = message.text
        product_id: int | None = validate_product_id(user_msg)

        if product_id:
            deleted: Subscription | None = await self.db.delete_subscription(state.user, product_id)
            if deleted is None:
                await message.answer(Msg.product_deleted_not_found(product_id))
            else:
                with transferring_file(deleted.product.img) as photo:
                    await message.answer_photo(
                        photo=photo,
                        caption=Msg.product_deleted(product_id)
                    )
            await state.finish()
        else:
            await message.answer(Msg.INVALID_PRINTED_PRODUCT)
