from collections.abc import Sequence

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from core.tg.buttons import (
    ACTIONS_ON_NOTIFY,
    ACTIONS_WITH_PRODUCT,
    ACTIONS_WITH_SUBSCRIPTIONS_W_NAV,
    ACTIONS_WITH_SUBSCRIPTIONS_W_NAV_LEFT_DISABLED,
    ACTIONS_WITH_SUBSCRIPTIONS_W_NAV_RIGHT_DISABLED,
    ACTIONS_WITH_SUBSCRIPTIONS_WO_NAV,
    AVAILABLE_ACTIONS,
    AVAILABLE_ACTIONS_W_EMPTY_SUBS,
)
from core.wb import form_url_from_product_id
from db.queries import SubscriptionsInfo
from utils.iterable import get_batches


class RowKeyboard(InlineKeyboardMarkup):
    def __init__(
        self,
        row_width: int = 3,
        row_size: int = 1,
        inline_keyboard: list[list[InlineKeyboardButton]] | None = None,
        buttons: Sequence[InlineKeyboardButton] | None = None,
        **kwargs: dict,
    ) -> None:
        super().__init__(row_width, inline_keyboard, **kwargs)
        if buttons is None:
            return
        for buttons_batch in get_batches(buttons, row_size):
            self.row(*buttons_batch)


class MenuKeyboard(RowKeyboard):
    def __init__(self) -> None:
        super().__init__(buttons=AVAILABLE_ACTIONS)


class MenuKeyboardWEmptySubs(RowKeyboard):
    def __init__(self) -> None:
        super().__init__(buttons=AVAILABLE_ACTIONS_W_EMPTY_SUBS)


class ProductKeyboard(RowKeyboard):
    def __init__(self) -> None:
        super().__init__(buttons=ACTIONS_WITH_PRODUCT)


class SubsNavigationKeyboard(InlineKeyboardMarkup):
    def __init__(self, subs: SubscriptionsInfo, product_id: int) -> None:
        super().__init__()
        buttons = [
            (
                InlineKeyboardButton(
                    text='Открыть карточку товара',
                    callback_data='open_product_card',
                    url=form_url_from_product_id(product_id),
                ),
            )
        ]
        if subs.subs_length > 1:
            if subs.current_position == 0:
                buttons += ACTIONS_WITH_SUBSCRIPTIONS_W_NAV_LEFT_DISABLED
            elif subs.current_position == subs.subs_cnt_by_user - 1:
                buttons += ACTIONS_WITH_SUBSCRIPTIONS_W_NAV_RIGHT_DISABLED
            else:
                buttons += ACTIONS_WITH_SUBSCRIPTIONS_W_NAV
        else:
            buttons += ACTIONS_WITH_SUBSCRIPTIONS_WO_NAV

        for buttons_batch in buttons:
            self.row(*buttons_batch)


class OnSubNotifyKeyboard(RowKeyboard):
    def __init__(self) -> None:
        super().__init__(buttons=ACTIONS_ON_NOTIFY)
