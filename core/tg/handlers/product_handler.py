from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from core.tg.buttons import (
    ACTIONS_W_PRODUCT_IF_EXIST_SUBSCRIPTION_AND_CHOSEN_W_THR,
    ACTIONS_W_PRODUCT_IF_EXIST_SUBSCRIPTION_AND_CHOSEN_WO_THR,
    MENU_BTN,
)
from core.tg.files import transferring_file
from core.tg.handlers.base_handler import BaseHandler
from core.tg.keyboards import ProductKeyboard, RowKeyboard
from core.tg.message_texts import Messages as Msg
from core.tg.notifier_state import NotifierState
from core.tg.storage import Context
from core.wb.wb_parser import WbParser, WbProduct
from db.queries import Subscription
from schemas.product import Product
from utils.validators import validate_product_id


class ProductHandler(BaseHandler):
    def register_handlers(self) -> None:
        self.dp.register_callback_query_handler(self.ask_product_id, text='ask_product_id')
        self.dp.register_message_handler(
            self.ask_action_with_product,
            state=NotifierState.waiting_product_id.state
        )

    @staticmethod
    async def ask_product_id(call: CallbackQuery, state: FSMContext) -> None:
        """"""
        keyboard = InlineKeyboardMarkup()
        keyboard.add(MENU_BTN)

        await state.set_state(NotifierState.waiting_product_id.state)

        await call.message.edit_text(Msg.PRINT_PRODUCT, reply_markup=keyboard)
        await call.answer()

    async def ask_action_with_product(self, message: Message, state: Context) -> None:
        """"""

        product_id: int | None = validate_product_id(message.text)
        if product_id is None:
            await message.answer(Msg.INVALID_PRINTED_PRODUCT)
            return

        products: dict[int, WbProduct] = await WbParser([product_id]).get_wb_products()
        wb_product: WbProduct | None = products.get(product_id)
        if wb_product is None or wb_product.empty:
            raise Exception(f'Не удалось прочитать товар "{product_id}"!')

        subscription: Subscription = await self.db.get_subscription_by_user_n_product(
            user_id=message.from_user.id,
            product_id=product_id
        )

        #   Нет подсписки - добавим
        #   FIXME: Убрать костыль с созданием Product
        if subscription.empty:
            await message.answer(
                text=Msg.current_product_price(
                    Product(ID=wb_product.id, Price=wb_product.price, Img=b'', Title=wb_product.title)
                ),
                reply_markup=ProductKeyboard()
            )

            await state.storage.write_wb_product(state.user, state.chat, wb_product)
            await state.set_state(NotifierState.waiting_action_w_product.state)
            return

        #   Уже есть подписка - показываем ее
        if subscription.user_product and subscription.user_product.added:
            #   Установлен порог уведомления
            if subscription.user_product.price_threshold:
                with transferring_file(subscription.product.img) as photo:
                    await message.answer_photo(
                        photo=photo,
                        caption=Msg.current_product_price_w_exist_subscription_w_thr(
                            subscription
                        ),
                        reply_markup=RowKeyboard(
                            btns=ACTIONS_W_PRODUCT_IF_EXIST_SUBSCRIPTION_AND_CHOSEN_W_THR
                        )
                    )
            #   Уведомление при любом снижении
            else:
                with transferring_file(subscription.product.img) as photo:
                    await message.answer_photo(
                        photo=photo,
                        caption=Msg.current_product_price_w_exist_subscription_wo_thr(
                            subscription
                        ),
                        reply_markup=RowKeyboard(
                            btns=ACTIONS_W_PRODUCT_IF_EXIST_SUBSCRIPTION_AND_CHOSEN_WO_THR
                        )
                    )

            await state.storage.write_wb_product(state.user, state.chat, wb_product)
            await state.set_state(NotifierState.waiting_action_w_product_for_exist.state)
            return


