from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from loguru import logger

from core.schemas.product import Product
from core.schemas.sub_product import SubProduct, SubProductCollection
from core.services.subscription import SubscriptionService
from core.tg.buttons import MENU_BTN
from core.tg.files import transferring_file
from core.tg.message_texts import Messages
from core.tg.notifier_state import NotifierState
from core.tg.storage import Context

router = Router(name='del_sub_router')


@router.callback_query(F.data == 'delete_cur_subscribe')
async def delete_cur_sub(
    call: CallbackQuery, state: Context, sub_service: SubscriptionService
) -> None:
    subprod_collection: SubProductCollection = await state.storage.get_subs_info(state.key)
    cur_sub: SubProduct = subprod_collection.sub_by_cur_pos

    deleted: SubProduct | None = await sub_service.delete_sub(state.key.user_id, cur_sub.product.id)
    if deleted is None:
        await call.answer(Messages.product_deleted_not_found(cur_sub.product))
        await state.clear()
        return

    with transferring_file(deleted.product.img) as photo:
        await call.message.answer_photo(
            photo=photo, caption=Messages.product_deleted(cur_sub.product)
        )
    await state.clear()


@router.callback_query(F.data == 'delete_subscribe')
async def delete_subscribe(call: CallbackQuery, state: Context) -> None:
    await state.set_state(NotifierState.waiting_product_id_for_del_subscribe.state)

    await call.message.answer(
        Messages.PRINT_PRODUCT, reply_markup=InlineKeyboardMarkup(inline_keyboard=[[MENU_BTN]])
    )
    await call.answer()


@router.message(NotifierState.waiting_product_id_for_del_subscribe)
async def delete_subscribe_for(
    message: Message, state: Context, sub_service: SubscriptionService
) -> None:
    if not message.text:
        logger.warning(f'Пустое сообщение ({message.text})!')
        await message.answer(Messages.INVALID_PRINTED_PRODUCT)
        await state.clear()
        return

    product_id, _ = sub_service.product_service.validate_product_id(message.text)
    if product_id is None:
        logger.warning(f'Некорректный ввод товара ({message.text})!')
        await message.answer(Messages.INVALID_PRINTED_PRODUCT)
        await state.clear()
        return

    deleted: SubProduct | None = await sub_service.delete_sub(state.key.user_id, product_id)
    if deleted is None:
        product: Product = await sub_service.product_service.get_product(product_id)
        await message.answer(Messages.product_deleted_not_found(product))
        await state.clear()
        return

    with transferring_file(deleted.product.img) as photo:
        await message.answer_photo(photo=photo, caption=Messages.product_deleted(deleted.product))
    await state.clear()
