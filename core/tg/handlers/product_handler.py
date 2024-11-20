from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from core.schemas.product import Product
from core.schemas.sub_product import SubProduct
from core.services.subscription import SubscriptionService
from core.services.wb import WbService
from core.tg.files import transferring_file
from core.tg.keyboards import (
    MenuBtnKeyboard,
    ProductActionsWOThr,
    ProductActionsWThr,
    ProductKeyboard,
)
from core.tg.message_texts import Messages
from core.tg.notifier_state import NotifierState
from core.tg.storage import Context
from logger import logger as loguru_logger

router = Router(name='product_router')


@router.callback_query(F.data == 'ask_product_id')
async def ask_product_id2(call: CallbackQuery, state: Context) -> None:
    await state.set_state(NotifierState.waiting_product_id.state)
    await call.message.edit_text(Messages.PRINT_PRODUCT, reply_markup=MenuBtnKeyboard())
    await call.answer()


@router.message(NotifierState.waiting_product_id)
async def ask_action_with_product(
    message: Message, state: Context, sub_service: SubscriptionService, wb_service: WbService
) -> None:
    if not message.text:
        loguru_logger.warning(f'Пустое сообщение ({message.text})!')
        await message.answer(Messages.INVALID_PRINTED_PRODUCT)
        await state.clear()
        return

    product_id: int | None = sub_service.product_service.validate_product_id(message.text)
    if product_id is None:
        loguru_logger.warning(f'Некорректный ввод товара ({message.text})!')
        await message.answer(Messages.INVALID_PRINTED_PRODUCT)
        await state.clear()
        return

    product: Product | None = await wb_service.try_get_product(product_id)
    if product is None:
        await state.clear()
        raise Exception(f'Не удалось прочитать товар "{product_id}"!')

    subscription: SubProduct | None = await sub_service.get_sub_by_user_product(
        user_id=state.key.user_id, product_id=product_id
    )

    #   Нет подсписки - предлодим что с ней сделать
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
