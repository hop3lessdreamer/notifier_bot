from aiogram import F, Router
from aiogram.types import CallbackQuery

from core.tg.keyboards import ProductKeyboard
from core.tg.notifier_state import NotifierState
from core.tg.storage import Context

router = Router(name='on_notify_router')


@router.callback_query(F.data == 'change_threshold_on_notify')
async def change_threshold_on_notify(call: CallbackQuery, state: Context) -> None:
    await call.message.edit_reply_markup(reply_markup=ProductKeyboard())
    await state.set_state(NotifierState.waiting_action_w_product.state)
