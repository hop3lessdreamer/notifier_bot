from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from core.tg.buttons import MENU_BTN
from core.tg.files import transferring_file
from core.tg.handlers.base_handler import BaseHandler
from core.tg.message_texts import Messages as Msg
from core.tg.notifier_state import NotifierState
from core.tg.storage import Context
from db.queries import Subscription
from logger import loguru_logger
from utils.validators import validate_wb_product_id


class DeleteSubscriptionHandlers(BaseHandler):
    def register_handlers(self) -> None:
        self.dp.register_callback_query_handler(self.delete_subscribe, text='delete_subscribe')
        self.dp.register_message_handler(
            self.delete_subscribe_for,
            state=NotifierState.waiting_product_id_for_del_subscribe.state,
        )

    @staticmethod
    async def delete_subscribe(call: CallbackQuery, state: Context) -> None:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(MENU_BTN)

        await state.set_state(NotifierState.waiting_product_id_for_del_subscribe.state)

        await call.message.answer(Msg.PRINT_PRODUCT, reply_markup=keyboard)
        await call.answer()

    async def delete_subscribe_for(self, message: Message, state: Context) -> None:
        product_id: int | None = validate_wb_product_id(message.text)
        if product_id is None:
            loguru_logger.warning(f'Некорректный ввод товара ({message.text})!')
            await message.answer(Msg.INVALID_PRINTED_PRODUCT)
            await state.finish()
            return

        deleted: Subscription | None = await self.db.delete_subscription(state.user, product_id)
        if deleted is None:
            await message.answer(Msg.product_deleted_not_found(product_id))
            await state.finish()
            return

        with transferring_file(deleted.product.img) as photo:
            await message.answer_photo(photo=photo, caption=Msg.product_deleted(product_id))
        await state.finish()
