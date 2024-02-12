from _decimal import Decimal
from aiogram.types import CallbackQuery, Message

from core.tg.files import transferring_file
from core.tg.handlers.subscription_handler import SubscriptionHandlers
from core.tg.message_texts import Messages as Msg
from core.tg.notifier_state import NotifierState
from core.tg.storage import Context
from core.wb.wb_parser import WbProduct
from db.queries import Subscription
from utils.transform_types import get_decimal, get_percents


class SubscriptionExistingHandlers(SubscriptionHandlers):

    def register_handlers(self) -> None:
        #   wo threshold
        self.dp.register_callback_query_handler(
            self.subscribe_wo_threshold,
            text='wo_threshold_for_exist',
            state=NotifierState.waiting_action_w_product_for_exist.state
        )

        #   w threshold
        self.dp.register_callback_query_handler(
            self.set_threshold_for_exist,
            text='set_threshold_for_exist',
            state=NotifierState.waiting_action_w_product_for_exist.state
        )
        self.dp.register_message_handler(
            self.subscribe_w_threshold, state=NotifierState.waiting_threshold_for_exist.state
        )

        #   w threshold in percents
        self.dp.register_callback_query_handler(
            self.set_threshold_in_percents_for_exist,
            text='set_threshold_in_percents_for_exist',
            state=NotifierState.waiting_action_w_product_for_exist.state
        )
        self.dp.register_message_handler(
            self.subscribe_w_threshold_in_percents, state=NotifierState.waiting_threshold_in_percents_for_exist.state
        )

    async def subscribe_wo_threshold(self, call: CallbackQuery, state: Context) -> None:
        """"""

        wb_product: WbProduct = await state.storage.get_wb_product(state.user, state.chat)
        if wb_product.empty:
            raise ValueError('Не удалось получить информацию о продукте из хранилища!')

        subscription: Subscription = await self.db.change_subscription_threshold(
            user_id=state.user,
            product_id=wb_product.id,
            threshold=wb_product.price
        )

        with transferring_file(subscription.product.img) as photo:
            await call.message.answer_photo(
                photo=photo,
                caption=Msg.product_added(wb_product.title)
            )

        await state.finish()
        await call.answer()

    @staticmethod
    async def set_threshold_for_exist(call: CallbackQuery, state: Context) -> None:
        """"""

        await call.message.answer(Msg.PRINT_THRESHOLD)
        await state.set_state(NotifierState.waiting_threshold_for_exist.state)
        await call.answer()

    async def subscribe_w_threshold(self, message: Message, state: Context) -> None:
        """"""

        wb_product: WbProduct = await state.storage.get_wb_product(state.user, state.chat)
        if wb_product.empty:
            raise ValueError('Не удалось получить информацию о продукте из хранилища!')

        user_id: int = message.from_user.id

        price_threshold: Decimal | None = get_decimal(message.text, precision=2)
        if not price_threshold:
            raise ValueError('Некорректный ввод цены!')

        subscription: Subscription = await self.db.change_subscription_threshold(
            user_id,
            wb_product.id,
            price_threshold
        )

        with transferring_file(subscription.product.img) as photo:
            await message.answer_photo(
                photo=photo,
                caption=Msg.product_added_w_threshold(
                    wb_product,
                    subscription.user_product.price_threshold
                )
            )

        await state.finish()

    @staticmethod
    async def set_threshold_in_percents_for_exist(call: CallbackQuery, state: Context) -> None:
        """"""

        await call.message.answer(Msg.PRINT_THRESHOLD_IN_PERCENT)
        await state.set_state(NotifierState.waiting_threshold_in_percents_for_exist.state)
        await call.answer()

    async def subscribe_w_threshold_in_percents(self, message: Message, state: Context) -> None:
        """"""

        user_id: int = message.from_user.id
        wb_product: WbProduct = await state.storage.get_wb_product(state.user, state.chat)
        if wb_product.empty:
            raise ValueError('Не удалось получить информацию о продукте из хранилища!')

        percents: float | None = get_percents(message.text)
        if not percents:
            raise ValueError('Некорректный ввод процентов!')

        threshold: Decimal = get_decimal(
            wb_product.rounded_price * get_decimal(1 - percents / 100),
            2
        )
        if threshold is None:
            raise ValueError('Не удалось рассчитать цену для уведомления!')

        subscription: Subscription = await self.db.change_subscription_threshold(
            user_id,
            wb_product.id,
            threshold
        )

        with transferring_file(subscription.product.img) as photo:
            await message.answer_photo(
                photo=photo,
                caption=Msg.product_added_w_threshold_in_percent(wb_product, threshold)
            )

        await state.finish()
