from aiogram.types import CallbackQuery, InputMediaPhoto

from core.tg.buttons import (
    ACTIONS_W_PRODUCT_IF_EXIST_SUBSCRIPTION_AND_CHOSEN_W_THR,
    ACTIONS_W_PRODUCT_IF_EXIST_SUBSCRIPTION_AND_CHOSEN_WO_THR,
)
from core.tg.files import transferring_file
from core.tg.handlers.base_handler import BaseHandler
from core.tg.keyboards import MenuKeyboard, RowKeyboard, SubsNavigationKeyboard
from core.tg.message_texts import Messages as Msg
from core.tg.notifier_state import NotifierState
from core.tg.storage import Context
from db.queries import Subscription, SubscriptionsInfo
from logger import loguru_logger


class ShowSubscriptionsHandlers(BaseHandler):
    def register_handlers(self) -> None:
        self.dp.register_callback_query_handler(self.show_subscriptions, text='show_subscriptions')
        self.dp.register_callback_query_handler(self.open_product_card, text='open_product_card')
        self.dp.register_callback_query_handler(self.delete_subscribe, text='delete_subscribe')
        self.dp.register_callback_query_handler(self.change_threshold, text='change_threshold')
        self.dp.register_callback_query_handler(self.prev_product_card, text='prev_product')
        self.dp.register_callback_query_handler(self.next_product_card, text='next_product')
        self.dp.register_callback_query_handler(self.empty_callback, text='disabled')

    async def empty_callback(self) -> None: ...

    async def show_subscriptions(self, call: CallbackQuery, state: Context) -> None:
        subscriptions_info: SubscriptionsInfo = await self.db.get_subscriptions_by_user(state.user)

        await state.storage.init_subs(state.user, state.chat, subscriptions_info)

        if subscriptions_info.empty:
            await call.message.answer(Msg.subscriptions_not_found(), reply_markup=MenuKeyboard())
        else:
            with transferring_file(subscriptions_info.first_sub.product.img) as photo:
                await call.message.answer_photo(
                    photo=photo,
                    caption=Msg.subscription(subscriptions_info),
                    reply_markup=SubsNavigationKeyboard(
                        subs=subscriptions_info,
                        product_id=subscriptions_info.first_sub.product.id
                    )
                )

        await call.answer()

    async def open_product_card(self, _call: CallbackQuery, _state: Context) -> None: ...

    async def delete_subscribe(self, call: CallbackQuery, state: Context) -> None:
        subs_info: SubscriptionsInfo = await state.storage.get_subs_info(state.user, state.chat)
        if subs_info.empty or not subs_info.sub_by_cur_pos:
            await call.message.answer(Msg.subscriptions_not_found(), reply_markup=MenuKeyboard())
            loguru_logger.error('Не удалось получить подписки из state.storage!')
            return

        await self.db.delete_subscription(
            user_id=subs_info.sub_by_cur_pos.user_product.user_id,
            product_id=subs_info.sub_by_cur_pos.product.id
        )

        deleted_sub: Subscription = subs_info.del_sub_by_cur_pos()

        if subs_info.empty:
            await call.message.delete()
            await call.message.answer(Msg.info_about_deletion(deleted_sub))
            await call.message.answer(Msg.subscriptions_not_found_after_deletion())
        else:
            with transferring_file(subs_info.sub_by_cur_pos.product.img) as photo:
                await call.message.edit_media(
                    InputMediaPhoto(
                        media=photo,
                        caption=Msg.subscription(subs_info)
                    ),
                    reply_markup=SubsNavigationKeyboard(
                        subs=subs_info,
                        product_id=deleted_sub.product.id
                    )
                )
            await call.message.answer(Msg.info_about_deletion(deleted_sub))

            await state.storage.write_subs(state.user, state.chat, subs_info)

    @staticmethod
    async def change_threshold(call: CallbackQuery, state: Context) -> None:
        subs_info: SubscriptionsInfo = await state.storage.get_subs_info(state.user, state.chat)
        if subs_info.empty or not subs_info.sub_by_cur_pos:
            loguru_logger.error('Не удалось получить подписки из state.storage!')
            return

        if subs_info.sub_by_cur_pos.product.price \
                != subs_info.sub_by_cur_pos.user_product.price_threshold:
            await call.message.edit_caption(
                caption=Msg.current_product_price_w_exist_subscription_w_thr(
                    subs_info.sub_by_cur_pos
                ),
                reply_markup=RowKeyboard(
                    btns=ACTIONS_W_PRODUCT_IF_EXIST_SUBSCRIPTION_AND_CHOSEN_W_THR
                )
            )

        else:
            await call.message.edit_caption(
                caption=Msg.current_product_price_w_exist_subscription_wo_thr(
                    subs_info.sub_by_cur_pos
                ),
                reply_markup=RowKeyboard(
                    btns=ACTIONS_W_PRODUCT_IF_EXIST_SUBSCRIPTION_AND_CHOSEN_WO_THR
                )
            )

        await state.storage\
            .write_wb_product(state.user, state.chat, subs_info.wb_prod_from_sub_by_cur_pos)
        await state.set_state(NotifierState.waiting_action_w_product_for_exist.state)

    @staticmethod
    async def prev_product_card(call: CallbackQuery, state: Context) -> None:
        subs_info: SubscriptionsInfo = await state.storage.get_subs_info(state.user, state.chat)
        if subs_info.empty or not subs_info.sub_by_cur_pos or subs_info.current_position == 0:
            loguru_logger.error('Не удалось получить подписки из state.storage!')
            return

        subs_info.go_to_prev_pos()

        with transferring_file(subs_info.sub_by_cur_pos.product.img) as photo:
            await call.message.edit_media(
                InputMediaPhoto(
                    media=photo,
                    caption=Msg.subscription(subs_info)
                ),
                reply_markup=SubsNavigationKeyboard(
                    subs=subs_info,
                    product_id=subs_info.sub_by_cur_pos.product.id
                )
            )

        await state.storage.write_subs(state.user, state.chat, subs_info)

    async def next_product_card(self, call: CallbackQuery, state: Context) -> None:
        subs_info: SubscriptionsInfo = await state.storage.get_subs_info(state.user, state.chat)
        if subs_info.empty or not subs_info.sub_by_cur_pos:
            loguru_logger.error('Не удалось получить подписки из state.storage!')
            return

        await subs_info.go_to_next_pos(user_id=state.user, db_connection=self.db)

        with transferring_file(subs_info.sub_by_cur_pos.product.img) as photo:
            await call.message.edit_media(
                InputMediaPhoto(
                    media=photo,
                    caption=Msg.subscription(subs_info)
                ),
                reply_markup=SubsNavigationKeyboard(
                    subs=subs_info,
                    product_id=subs_info.sub_by_cur_pos.product.id
                )
            )

        await state.storage.write_subs(state.user, state.chat, subs_info)
