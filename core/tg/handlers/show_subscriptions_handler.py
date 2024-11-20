from aiogram import F, Router
from aiogram.types import CallbackQuery, InputMediaPhoto

from core.schemas.sub_product import SubProduct, SubProductCollection
from core.services.subscription import SubscriptionService
from core.tg.files import transferring_file
from core.tg.keyboards import (
    MenuKeyboard,
    ProductActionsWOThr,
    ProductActionsWThr,
    SubsNavigationKeyboard,
)
from core.tg.message_texts import Messages as Msg
from core.tg.notifier_state import NotifierState
from core.tg.storage import Context
from logger import logger as loguru_logger

router = Router(name='show_sub_router')


@router.callback_query(F.data == 'disabled')
def empty_callback() -> None:
    ...


@router.callback_query(F.data == 'show_subscriptions')
async def show_subscriptions(
    call: CallbackQuery, state: Context, sub_service: SubscriptionService
) -> None:
    sub_collection: SubProductCollection = await state.storage.init_subs(
        state.key,
        await sub_service.get_sub_by_user(state.key.user_id),
        await sub_service.sub_cnt_by_user(state.key.user_id),
    )
    if sub_collection.empty:
        await call.message.answer(Msg.subscriptions_not_found(), reply_markup=MenuKeyboard())
    else:
        if sub_collection.first_sub is None:
            raise ValueError('Не удалось получить первую подписку!')
        with transferring_file(sub_collection.first_sub.product.img) as photo:
            await call.message.answer_photo(
                photo=photo,
                caption=Msg.subscription(sub_collection),
                reply_markup=SubsNavigationKeyboard(subs=sub_collection),
            )

    await call.answer()


@router.callback_query(F.data == 'open_product_card')
async def open_product_card(_call: CallbackQuery, _state: Context) -> None:
    ...


@router.callback_query(F.data == 'delete_subscribe')
async def delete_subscribe(
    call: CallbackQuery, state: Context, sub_service: SubscriptionService
) -> None:
    sub_collection: SubProductCollection = await state.storage.get_subs_info(state.key)
    if not sub_collection.sub_by_cur_pos:
        await call.message.answer(Msg.subscriptions_not_found(), reply_markup=MenuKeyboard())
        loguru_logger.error('Не удалось получить подписки из state.storage!')
        return

    await sub_service.delete_sub(
        user_id=state.key.user_id,
        product_id=sub_collection.sub_by_cur_pos.product.id,
    )
    deleted_sub: SubProduct = sub_collection.del_sub_by_cur_pos()

    with transferring_file(deleted_sub.product.img) as photo:
        await call.message.edit_media(
            InputMediaPhoto(media=photo, caption=Msg.subscription(sub_collection)),
            reply_markup=SubsNavigationKeyboard(
                subs=sub_collection, product_id=deleted_sub.product.id
            ),
        )
    await call.message.answer(Msg.info_about_deletion(deleted_sub))
    await state.storage.write_subs(state.key, sub_collection)


@router.callback_query(F.data == 'change_threshold')
async def change_threshold(call: CallbackQuery, state: Context) -> None:
    subprod_collection: SubProductCollection = await state.storage.get_subs_info(state.key)
    if subprod_collection.sub_by_cur_pos.subscription.price_threshold:
        await call.message.edit_caption(
            caption=Msg.current_product_price_w_exist_subscription_w_thr(
                subprod_collection.sub_by_cur_pos
            ),
            reply_markup=ProductActionsWThr(),
        )

    else:
        await call.message.edit_caption(
            caption=Msg.current_product_price_w_exist_subscription_wo_thr(
                subprod_collection.sub_by_cur_pos
            ),
            reply_markup=ProductActionsWOThr(),
        )

    await state.storage.write_product(state.key, subprod_collection.prod_by_cur_pos)
    await state.set_state(NotifierState.waiting_action_w_product_for_exist.state)


@router.callback_query(F.data == 'prev_product')
async def prev_product_card(
    call: CallbackQuery, state: Context, sub_service: SubscriptionService
) -> None:
    sub_collection: SubProductCollection = await state.storage.get_subs_info(state.key)
    if not sub_collection.sub_by_cur_pos:
        loguru_logger.error('Не удалось получить подписки из state.storage!')
        return

    sub_service.shift_backward_pos_by_sub_collection(sub_collection)
    with transferring_file(sub_collection.sub_by_cur_pos.product.img) as photo:
        await call.message.edit_media(
            InputMediaPhoto(media=photo, caption=Msg.subscription(sub_collection)),
            reply_markup=SubsNavigationKeyboard(subs=sub_collection),
        )

    await state.storage.write_subs(state.key, sub_collection)


@router.callback_query(F.data == 'next_product')
async def next_product_card(
    call: CallbackQuery, state: Context, sub_service: SubscriptionService
) -> None:
    sub_collection: SubProductCollection = await state.storage.get_subs_info(state.key)
    if not sub_collection.sub_by_cur_pos:
        loguru_logger.error('Не удалось получить подписки из state.storage!')
        return

    await sub_service.shift_forward_pos_by_sub_collection(sub_collection, state.key.user_id)

    with transferring_file(sub_collection.sub_by_cur_pos.product.img) as photo:
        await call.message.edit_media(
            InputMediaPhoto(media=photo, caption=Msg.subscription(sub_collection)),
            reply_markup=SubsNavigationKeyboard(subs=sub_collection),
        )

    await state.storage.write_subs(state.key, sub_collection)
