from decimal import Decimal

from aiogram.types import CallbackQuery, Message

from core.tg.files import transferring_file
from core.tg.handlers.base_handler import BaseHandler
from core.tg.message_texts import Messages as Msg
from core.tg.notifier_state import NotifierState
from core.tg.storage import Context
from core.wb.wb_img_downloader import WbImgDownloader
from core.wb.wb_parser import WbProduct
from schemas.product import Product
from utils.transform_types import get_decimal, get_percents
from utils.types import b64


class SubscriptionHandlers(BaseHandler):
    def register_handlers(self) -> None:
        #   wo threshold
        self.dp.register_callback_query_handler(
            self.subscribe_wo_threshold,
            text='wo_threshold',
            state=NotifierState.waiting_action_w_product.state,
        )

        #   w threshold
        self.dp.register_callback_query_handler(
            self.set_threshold,
            text='set_threshold',
            state=NotifierState.waiting_action_w_product.state,
        )
        self.dp.register_message_handler(
            self.subscribe_w_threshold, state=NotifierState.waiting_threshold.state
        )

        #   w threshold in percents
        self.dp.register_callback_query_handler(
            self.set_threshold_in_percents,
            text='set_threshold_in_percents',
            state=NotifierState.waiting_action_w_product.state,
        )
        self.dp.register_message_handler(
            self.subscribe_w_threshold_in_percents,
            state=NotifierState.waiting_threshold_in_percents.state,
        )

    async def subscribe_wo_threshold(self, call: CallbackQuery, state: Context) -> None:
        """"""

        wb_product: WbProduct | None = await state.storage.get_wb_product(state.user, state.chat)
        if wb_product is None:
            raise ValueError('Не удалось получить информацию о продукте из хранилища!')

        product_img: b64 = await WbImgDownloader(wb_product.id).download()  # type: ignore

        product: Product = Product(
            ID=wb_product.id,
            Price=get_decimal(wb_product.price, 2),
            Img=product_img,
            Title=wb_product.title,
        )

        await self.db.add_subscription(state.user, product, product.price)
        with transferring_file(product_img) as photo:
            await call.message.answer_photo(photo=photo, caption=Msg.product_added(product.title))

        await state.finish()
        await call.answer()

    @staticmethod
    async def set_threshold(call: CallbackQuery, state: Context) -> None:
        """"""

        await call.message.answer(Msg.PRINT_THRESHOLD)
        await state.set_state(NotifierState.waiting_threshold.state)
        await call.answer()

    async def subscribe_w_threshold(self, message: Message, state: Context) -> None:
        """"""

        wb_product: WbProduct | None = await state.storage.get_wb_product(state.user, state.chat)
        if wb_product is None:
            raise ValueError('Не удалось получить информацию о продукте из хранилища!')

        user_id: int = message.from_user.id

        product_img: bytes = await WbImgDownloader(wb_product.id).download()

        product: Product = Product(
            ID=wb_product.id,
            Price=get_decimal(wb_product.price, 2),
            Img=product_img,
            Title=wb_product.title,
        )

        price_threshold: Decimal | None = get_decimal(message.text)
        if not price_threshold:
            raise ValueError('Некорректный ввод цены!')

        await self.db.add_subscription(user_id, product, price_threshold)

        with transferring_file(product_img) as photo:
            await message.answer_photo(
                photo=photo, caption=Msg.product_added_w_threshold(product, price_threshold)
            )

        await state.finish()

    @staticmethod
    async def set_threshold_in_percents(call: CallbackQuery, state: Context) -> None:
        """"""

        await call.message.answer(Msg.PRINT_THRESHOLD_IN_PERCENT)
        await state.set_state(NotifierState.waiting_threshold_in_percents.state)
        await call.answer()

    async def subscribe_w_threshold_in_percents(self, message: Message, state: Context) -> None:
        """"""

        wb_product: WbProduct | None = await state.storage.get_wb_product(state.user, state.chat)
        if wb_product is None:
            raise ValueError('Не удалось получить информацию о продукте из хранилища!')

        user_id: int = message.from_user.id

        product_img: bytes = await WbImgDownloader(wb_product.id).download()

        price: Decimal | None = get_decimal(wb_product.price, 2)
        if price is None:
            ValueError('Ошибка валидации цены на товар!')

        product: Product = Product(
            ID=wb_product.id,
            Price=price,
            Img=product_img,
            Title=wb_product.title,
        )

        percents: Decimal | None = get_percents(message.text)
        if not percents:
            raise ValueError('Некорректный ввод процентов!')

        threshold: Decimal | None = get_decimal(product.price * percents, 2)
        if not threshold:
            raise ValueError('Не удалось рассчитать цену для уведомления!')

        await self.db.add_subscription(user_id, product, threshold)

        with transferring_file(product_img) as photo:
            await message.answer_photo(
                photo=photo, caption=Msg.product_added_w_threshold_in_percent(wb_product, threshold)
            )

        await state.finish()
