from decimal import Decimal

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from core.schemas.product import Product
from core.services.subscription import SubscriptionService
from core.tg.files import transferring_file
from core.tg.message_texts import Messages as Msg
from core.tg.notifier_state import NotifierState
from core.tg.storage import Context
from utils.transform_types import get_decimal, get_percents, try_get_decimal

router = Router(name='sub_router')


@router.callback_query(NotifierState.waiting_action_w_product, F.data == 'wo_threshold')
async def subscribe_wo_threshold(
    call: CallbackQuery, state: Context, sub_service: SubscriptionService
) -> None:
    product: Product = await state.storage.get_product(state.key)
    await sub_service.subscribe_to_price_reduction(state.key.user_id, product)
    with transferring_file(product.img) as photo:
        await call.message.answer_photo(photo, caption=Msg.product_added(product.title))

    await call.answer()
    await state.clear()


@router.callback_query(NotifierState.waiting_action_w_product, F.data == 'set_threshold')
async def set_threshold(call: CallbackQuery, state: Context) -> None:
    await call.message.answer(Msg.PRINT_THRESHOLD)
    await state.set_state(NotifierState.waiting_threshold.state)
    await call.answer()


@router.message(NotifierState.waiting_threshold)
async def subscribe_w_threshold(
    message: Message, state: Context, sub_service: SubscriptionService
) -> None:
    product: Product = await state.storage.get_product(state.key)
    price_threshold: Decimal | None = try_get_decimal(message.text)
    if not price_threshold:
        raise ValueError('Некорректный ввод цены!')

    await sub_service.subscribe(state.key.user_id, product, price_threshold)

    with transferring_file(product.img) as photo:
        await message.answer_photo(
            photo=photo, caption=Msg.product_added_w_threshold(product, price_threshold)
        )
    await state.clear()


@router.callback_query(
    NotifierState.waiting_action_w_product, F.data == 'set_threshold_in_percents'
)
async def set_threshold_in_percents(call: CallbackQuery, state: Context) -> None:
    await call.message.answer(Msg.PRINT_THRESHOLD)
    await state.set_state(NotifierState.waiting_threshold_in_percents)
    await call.answer()


@router.message(NotifierState.waiting_threshold_in_percents)
async def subscribe_w_threshold_in_percents(
    message: Message, state: Context, sub_service: SubscriptionService
) -> None:
    product: Product = await state.storage.get_product(state.key)

    percents: Decimal | None = get_percents(message.text or '')
    if not percents:
        #   TODO: Сделать обработку сообщением пользователю!
        raise ValueError('Некорректный ввод процентов!')

    threshold: Decimal = get_decimal(product.price * percents, 2)
    await sub_service.subscribe(state.key.user_id, product, threshold)

    with transferring_file(product.img) as photo:
        await message.answer_photo(
            photo=photo, caption=Msg.product_added_w_threshold_in_percent(product, threshold)
        )

    await state.clear()
