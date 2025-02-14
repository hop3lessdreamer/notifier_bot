from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from loguru import logger

from core.schemas.product import MPType, Product
from core.schemas.sub_product import SubProduct
from core.services.ozon import OzonService
from core.services.subscription import SubscriptionService
from core.services.wb import WbService
from core.tg.files import transferring_file
from core.tg.keyboards import (
    ChooseMPType,
    MenuBtnKeyboard,
    ProductActionsWOThr,
    ProductActionsWThr,
    ProductKeyboard,
)
from core.tg.message_texts import Messages
from core.tg.notifier_state import NotifierState
from core.tg.storage import Context

router = Router(name='product_router')


@router.callback_query(F.data == 'ask_product_id')
async def ask_product_id(call: CallbackQuery, state: Context) -> None:
    await state.set_state(NotifierState.waiting_product_id.state)
    await call.message.edit_text(Messages.PRINT_PRODUCT, reply_markup=MenuBtnKeyboard())
    await call.answer()


@router.message(NotifierState.waiting_product_id)
async def ask_action_with_product(
    message: Message,
    state: Context,
    sub_service: SubscriptionService,
    wb_service: WbService,
    ozon_service: OzonService,
) -> None:
    if not message.text:
        logger.info(f'Пустое сообщение ({message.text})!')
        await message.answer(Messages.INVALID_PRINTED_PRODUCT)
        await state.clear()
        return

    product_id, prod_mp_type = sub_service.product_service.validate_product_id(message.text)
    if product_id is None:
        logger.info(f'Некорректный ввод товара ({message.text})!')
        await message.answer(Messages.INVALID_PRINTED_PRODUCT)
        await state.clear()
        return

    if prod_mp_type is None:
        logger.info(f'Нет mp_type для "{message.text}"')
        await message.answer(Messages.CHOOSE_MP_TYPE, reply_markup=ChooseMPType())
        await state.storage.write_prod_id(state.key, product_id)
        await state.set_state(None)
        return

    if prod_mp_type == MPType.WB:
        product: Product | None = await wb_service.try_get_product(product_id)
        if product is None:
            await state.clear()
            raise Exception(f'Не удалось прочитать товар "{product_id}"!')
    elif prod_mp_type == MPType.OZON:
        product = await ozon_service.try_get_product(product_id)
        if product is None:
            await state.clear()
            raise Exception(f'Не удалось прочитать товар "{product_id}"!')
    else:
        raise Exception(f'Неожиданный MPType "{prod_mp_type}"!')

    subscription: SubProduct | None = await sub_service.get_sub_by_user_product(
        user_id=state.key.user_id, product_id=product_id
    )

    #   Нет подсписки - предложим что с ней сделать
    if subscription is None:
        await message.answer(
            text=Messages.current_product_price(product),
            reply_markup=ProductKeyboard(),
        )
        await state.storage.write_product(state.key, product)
        await state.set_state(NotifierState.waiting_action_w_product.state)
        return

    #   Уже есть подписка - показываем ее
    if subscription.subscription and subscription.subscription.added:
        await _show_sub(message, subscription)

        await state.storage.write_product(state.key, product)
        await state.set_state(NotifierState.waiting_action_w_product_for_exist.state)
        return


@router.callback_query(F.data == 'wb_mp_type')
async def get_wb_prod(
    call: CallbackQuery, state: Context, sub_service: SubscriptionService, wb_service: WbService
) -> None:
    product_id: int = await state.storage.get_prod_id(state.key)
    product: Product | None = await wb_service.try_get_product(product_id)
    if product is None:
        await state.clear()
        raise Exception(f'Не удалось прочитать товар "{product_id}"!')

    subscription: SubProduct | None = await sub_service.get_sub_by_user_product(
        user_id=state.key.user_id, product_id=product_id
    )

    #   Нет подсписки - предложим что с ней сделать
    if subscription is None:
        await call.message.answer(
            text=Messages.current_product_price(product),
            reply_markup=ProductKeyboard(),
        )

        await state.storage.write_product(state.key, product)
        await state.set_state(NotifierState.waiting_action_w_product.state)
        return

    #   Уже есть подписка - показываем ее
    if subscription.subscription and subscription.subscription.added:
        await _show_sub(call.message, subscription)

        await state.storage.write_product(state.key, product)
        await state.set_state(NotifierState.waiting_action_w_product_for_exist.state)
        return


@router.callback_query(F.data == 'ozon_mp_type')
async def get_ozon_prod(
    call: CallbackQuery, state: Context, sub_service: SubscriptionService, ozon_service: OzonService
) -> None:
    product_id: int = await state.storage.get_prod_id(state.key)
    product: Product = await ozon_service.get_product(product_id)

    subscription: SubProduct | None = await sub_service.get_sub_by_user_product(
        user_id=state.key.user_id, product_id=product_id
    )
    #   Нет подсписки - предложим что с ней сделать
    if subscription is None:
        await call.message.answer(
            text=Messages.current_product_price(product),
            reply_markup=ProductKeyboard(),
        )

        await state.storage.write_product(state.key, product)
        await state.set_state(NotifierState.waiting_action_w_product.state)
        return

    #   Уже есть подписка - показываем ее
    if subscription.subscription and subscription.subscription.added:
        await _show_sub(call.message, subscription)

        await state.storage.write_product(state.key, product)
        await state.set_state(NotifierState.waiting_action_w_product_for_exist.state)
        return


async def _show_sub(msg: Message, sub: SubProduct) -> None:
    #   Установлен порог уведомления
    if sub.subscription.price_threshold:
        with transferring_file(sub.product.img) as photo:
            await msg.answer_photo(
                photo=photo,
                caption=Messages.current_product_price_w_exist_subscription_w_thr(sub),
                reply_markup=ProductActionsWThr(),
            )
            return

    #   Уведомление при любом снижении
    with transferring_file(sub.product.img) as photo:
        await msg.answer_photo(
            photo=photo,
            caption=Messages.current_product_price_w_exist_subscription_wo_thr(sub),
            reply_markup=ProductActionsWOThr(),
        )
