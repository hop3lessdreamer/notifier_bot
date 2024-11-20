from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from core.schemas.sub_product import SubProductCollection
from core.tg.buttons import (
    ACTIONS_ON_NOTIFY,
    ACTIONS_W_PRODUCT_IF_EXIST_SUBSCRIPTION_AND_CHOSEN_W_THR,
    ACTIONS_W_PRODUCT_IF_EXIST_SUBSCRIPTION_AND_CHOSEN_WO_THR,
    ACTIONS_WITH_PRODUCT,
    ACTIONS_WITH_SUBSCRIPTIONS_W_NAV,
    ACTIONS_WITH_SUBSCRIPTIONS_W_NAV_LEFT_DISABLED,
    ACTIONS_WITH_SUBSCRIPTIONS_W_NAV_RIGHT_DISABLED,
    ACTIONS_WITH_SUBSCRIPTIONS_WO_NAV,
    AVAILABLE_ACTIONS,
    AVAILABLE_ACTIONS_W_EMPTY_SUBS,
    AVAILABLE_MARKET_PLACES,
    MENU_BTN,
)
from core.wb import form_url_from_product_id


class MenuKeyboard(InlineKeyboardMarkup):
    def __init__(self) -> None:
        super().__init__(inline_keyboard=AVAILABLE_ACTIONS)


class MenuKeyboardWEmptySubs(InlineKeyboardMarkup):
    def __init__(self) -> None:
        super().__init__(inline_keyboard=AVAILABLE_ACTIONS_W_EMPTY_SUBS)


class ProductKeyboard(InlineKeyboardMarkup):
    def __init__(self) -> None:
        super().__init__(inline_keyboard=ACTIONS_WITH_PRODUCT)


class SubsNavigationKeyboard(InlineKeyboardMarkup):
    def __init__(self, subs: SubProductCollection, product_id: int | None = None) -> None:
        buttons: list[list[InlineKeyboardButton]] = [
            [
                InlineKeyboardButton(
                    text='Открыть карточку товара',
                    callback_data='open_product_card',
                    url=form_url_from_product_id(product_id or subs.sub_by_cur_pos.product.id),
                ),
            ]
        ]
        if subs.subs_length > 1:
            if subs.cur_pos == 0:
                buttons += ACTIONS_WITH_SUBSCRIPTIONS_W_NAV_LEFT_DISABLED
            elif subs.cur_pos == subs.total_sub_cnt - 1:
                buttons += ACTIONS_WITH_SUBSCRIPTIONS_W_NAV_RIGHT_DISABLED
            else:
                buttons += ACTIONS_WITH_SUBSCRIPTIONS_W_NAV
        else:
            buttons += ACTIONS_WITH_SUBSCRIPTIONS_WO_NAV

        super().__init__(inline_keyboard=buttons)


class OnSubNotifyKeyboard(InlineKeyboardMarkup):
    def __init__(self) -> None:
        super().__init__(inline_keyboard=ACTIONS_ON_NOTIFY)


class ProductActionsWThr(InlineKeyboardMarkup):
    def __init__(self) -> None:
        super().__init__(inline_keyboard=ACTIONS_W_PRODUCT_IF_EXIST_SUBSCRIPTION_AND_CHOSEN_W_THR)


class ProductActionsWOThr(InlineKeyboardMarkup):
    def __init__(self) -> None:
        super().__init__(inline_keyboard=ACTIONS_W_PRODUCT_IF_EXIST_SUBSCRIPTION_AND_CHOSEN_WO_THR)


class MenuBtnKeyboard(InlineKeyboardMarkup):
    def __init__(self) -> None:
        super().__init__(inline_keyboard=[[MENU_BTN]])


class MarketPlaceKeyboard(InlineKeyboardMarkup):
    def __init__(self) -> None:
        super().__init__(inline_keyboard=[AVAILABLE_MARKET_PLACES])
