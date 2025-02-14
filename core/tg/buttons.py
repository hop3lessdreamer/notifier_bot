""" Bot buttons """

from aiogram.types import InlineKeyboardButton

AVAILABLE_ACTIONS = [
    [InlineKeyboardButton(text='Следить за товаром', callback_data='ask_product_id')],
    [
        InlineKeyboardButton(
            text='Посмотреть отслеживаемые товары', callback_data='show_subscriptions'
        )
    ],
    [InlineKeyboardButton(text='Удалить отслеживаемый товар', callback_data='delete_subscribe')],
]

AVAILABLE_ACTIONS_W_EMPTY_SUBS = [
    [InlineKeyboardButton(text='Следить за товаром', callback_data='ask_product_id')],
]

ACTIONS_WITH_PRODUCT = [
    [InlineKeyboardButton(text='Уведомить при любом снижении цены', callback_data='wo_threshold')],
    [InlineKeyboardButton(text='Установить цену для уведомления', callback_data='set_threshold')],
    [
        InlineKeyboardButton(
            text='Установить цену для уведомления в процентах',
            callback_data='set_threshold_in_percents',
        )
    ],
]

ACTIONS_WITH_SUBSCRIPTIONS_WO_NAV = [
    [InlineKeyboardButton(text='Изменить порог уведомления', callback_data='change_threshold')],
    [InlineKeyboardButton(text='Удалить', callback_data='delete_cur_subscribe')],
]

ACTIONS_WITH_SUBSCRIPTIONS_W_NAV = ACTIONS_WITH_SUBSCRIPTIONS_WO_NAV + [
    [
        InlineKeyboardButton(text='<<', callback_data='prev_product'),
        InlineKeyboardButton(text='>>', callback_data='next_product'),
    ]
]


ACTIONS_WITH_SUBSCRIPTIONS_W_NAV_LEFT_DISABLED = ACTIONS_WITH_SUBSCRIPTIONS_WO_NAV + [
    [
        InlineKeyboardButton(text='🚫', callback_data='disabled'),
        InlineKeyboardButton(text='>>', callback_data='next_product'),
    ]
]


ACTIONS_WITH_SUBSCRIPTIONS_W_NAV_RIGHT_DISABLED = ACTIONS_WITH_SUBSCRIPTIONS_WO_NAV + [
    [
        InlineKeyboardButton(text='<<', callback_data='prev_product'),
        InlineKeyboardButton(text='🚫', callback_data='disabled'),
    ]
]

WO_THRESHOLD_FOR_EXIST_BTN = InlineKeyboardButton(
    text='Уведомить при любом снижении цены', callback_data='wo_threshold_for_exist'
)
SET_THRESHOLD_FOR_EXIST_BTN = InlineKeyboardButton(
    text='Изменить цену для уведомления', callback_data='set_threshold_for_exist'
)
SET_THRESHOLD_IN_PERCENTS_FOR_EXIST_BTN = InlineKeyboardButton(
    text='Изменить цену для уведомления в процентах',
    callback_data='set_threshold_in_percents_for_exist',
)
MENU_BTN = InlineKeyboardButton(text='Меню', callback_data='menu')


ACTIONS_W_PRODUCT_IF_EXIST_SUBSCRIPTION_AND_CHOSEN_WO_THR = [
    [SET_THRESHOLD_FOR_EXIST_BTN],
    [SET_THRESHOLD_IN_PERCENTS_FOR_EXIST_BTN],
    [MENU_BTN],
]


ACTIONS_W_PRODUCT_IF_EXIST_SUBSCRIPTION_AND_CHOSEN_W_THR = [
    [WO_THRESHOLD_FOR_EXIST_BTN],
    [SET_THRESHOLD_FOR_EXIST_BTN],
    [SET_THRESHOLD_IN_PERCENTS_FOR_EXIST_BTN],
    [MENU_BTN],
]


CHANGE_THRESHOLD_ON_NOTIFY = InlineKeyboardButton(
    text='Изменить цену для уведомления', callback_data='change_threshold_on_notify'
)

ACTIONS_ON_NOTIFY = [[CHANGE_THRESHOLD_ON_NOTIFY]]


WB_MP_TYPE = InlineKeyboardButton(text='Wildberries', callback_data='wb_mp_type')
OZON_MP_TYPE = InlineKeyboardButton(text='OZON', callback_data='ozon_mp_type')
MP_TYPES = [[WB_MP_TYPE, OZON_MP_TYPE]]
