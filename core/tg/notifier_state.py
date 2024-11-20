""" NotifierState """
from aiogram.fsm.state import State, StatesGroup


class NotifierState(StatesGroup):
    waiting_product_id = State()
    waiting_action_w_product = State()
    waiting_threshold = State()
    waiting_threshold_in_percents = State()
    waiting_product_id_for_del_subscribe = State()
    waiting_action_w_product_for_exist = State()
    waiting_threshold_for_exist = State()
    waiting_threshold_in_percents_for_exist = State()
