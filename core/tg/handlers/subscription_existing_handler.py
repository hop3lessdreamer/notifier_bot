from decimal import Decimal

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from core.schemas.product import Product
from core.schemas.sub_product import SubProduct
from core.services.subscription import SubscriptionService
from core.tg.files import transferring_file
from core.tg.message_texts import Messages as Msg
from core.tg.notifier_state import NotifierState
from core.tg.storage import Context
from utils.transform_types import get_decimal, get_percents, try_get_decimal

router = Router(name='sub_existing_router')


@router.callback_query(
    NotifierState.waiting_action_w_product_for_exist, F.data == 'wo_threshold_for_exist'
)
async def subscribe_wo_threshold(
    call: CallbackQuery, state: Context, sub_service: SubscriptionService
) -> None:
    product: Product = await state.storage.get_product(state.key)
    subscription: SubProduct = await sub_service.subscribe_to_price_reduction_for_exist(
        state.key.user_id, product
    )
    with transferring_file(subscription.product.img) as photo:
        await call.message.answer_photo(photo=photo, caption=Msg.product_added(product.title))

    await state.clear()
    await call.answer()


@router.callback_query(
    NotifierState.waiting_action_w_product_for_exist, F.data == 'set_threshold_for_exist'
)
async def set_threshold_for_exist(call: CallbackQuery, state: Context) -> None:
    await call.message.answer(Msg.PRINT_THRESHOLD)
    await state.set_state(NotifierState.waiting_threshold_for_exist.state)
    await call.answer()


@router.message(NotifierState.waiting_threshold_for_exist)
async def subscribe_w_threshold(
    message: Message, state: Context, sub_service: SubscriptionService
) -> None:
    product: Product = await state.storage.get_product(state.key)
    price_threshold: Decimal | None = try_get_decimal(message.text, precision=2)
    if not price_threshold:
        raise ValueError('Некорректный ввод цены!')

    sub: SubProduct = await sub_service.resubscribe(state.key.user_id, product.id, price_threshold)

    with transferring_file(sub.product.img) as photo:
        await message.answer_photo(
            photo=photo,
            caption=Msg.product_added_w_threshold(product, sub.subscription.price_threshold),
        )

    await state.clear()


@router.callback_query(
    NotifierState.waiting_action_w_product_for_exist,
    F.data == 'set_threshold_in_percents_for_exist',
)
async def set_threshold_in_percents_for_exist(call: CallbackQuery, state: Context) -> None:
    await call.message.answer(Msg.PRINT_THRESHOLD_IN_PERCENT)
    await state.set_state(NotifierState.waiting_threshold_in_percents_for_exist.state)
    await call.answer()


@router.message(NotifierState.waiting_threshold_in_percents_for_exist)
async def subscribe_w_threshold_in_percents(
    message: Message, state: Context, sub_service: SubscriptionService
) -> None:
    product: Product = await state.storage.get_product(state.key)
    percents: Decimal | None = get_percents(message.text or '')
    if not percents:
        raise ValueError('Некорректный ввод процентов!')

    threshold: Decimal = get_decimal(product.price * percents, 2)
    sub: SubProduct = await sub_service.resubscribe(state.key.user_id, product.id, threshold)

    with transferring_file(sub.product.img) as photo:
        await message.answer_photo(
            photo=photo, caption=Msg.product_added_w_threshold_in_percent(product, threshold)
        )

    await state.clear()
