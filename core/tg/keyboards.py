from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from core.tg.buttons import (
    ACTIONS_WITH_PRODUCT,
    ACTIONS_WITH_SUBSCRIPTIONS_W_NAV,
    ACTIONS_WITH_SUBSCRIPTIONS_WO_NAV,
    AVAILABLE_ACTIONS,
    AVAILABLE_ACTIONS_W_EMPTY_SUBS, ACTIONS_WITH_SUBSCRIPTIONS_W_NAV_LEFT_DISABLED,
    ACTIONS_WITH_SUBSCRIPTIONS_W_NAV_RIGHT_DISABLED,
)
from core.wb import form_url_from_product_id
from db.queries import SubscriptionsInfo
from utils.iterable import get_batches


class RowKeyboard(InlineKeyboardMarkup):
    def __init__(
            self,
            row_width: int = 3,
            row_size: int = 1,
            inline_keyboard=None,
            btns: list[InlineKeyboardButton] | None = None,
            **kwargs
    ) -> None:
        super().__init__(row_width, inline_keyboard, **kwargs)
        for buttons_batch in get_batches(btns, row_size):
            self.row(*buttons_batch)


class MenuKeyboard(RowKeyboard):
    def __init__(
            self,
            row_width: int = 3,
            row_size: int = 1,
            inline_keyboard=None,
            btns=AVAILABLE_ACTIONS,
            **kwargs
    ) -> None:
        super().__init__(row_width, row_size, inline_keyboard, btns=btns, **kwargs)


class MenuKeyboardWEmptySubs(MenuKeyboard):
    def __init__(
            self,
            row_width: int = 3,
            row_size: int = 1,
            inline_keyboard=None,
            btns=AVAILABLE_ACTIONS_W_EMPTY_SUBS,
            **kwargs
    ) -> None:
        super().__init__(row_width, row_size, inline_keyboard, btns=btns, **kwargs)


class ProductKeyboard(RowKeyboard):
    def __init__(
            self,
            row_width: int = 3,
            row_size: int = 1,
            inline_keyboard=None,
            **kwargs
    ) -> None:
        super().__init__(row_width, row_size, inline_keyboard, btns=ACTIONS_WITH_PRODUCT, **kwargs)


class SubsNavigationKeyboard(InlineKeyboardMarkup):
    def __init__(
            self,
            subs: SubscriptionsInfo,
            product_id: int,
            row_width: int = 3,
            inline_keyboard=None,
            **kwargs
    ) -> None:
        super().__init__(row_width, inline_keyboard, **kwargs)
        buttons = [(InlineKeyboardButton(
            text='Открыть карточку товара',
            callback_data='open_product_card',
            url=form_url_from_product_id(product_id)
        ),)]
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
