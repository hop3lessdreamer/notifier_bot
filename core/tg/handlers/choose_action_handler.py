from aiogram import F, Router
from aiogram.types import CallbackQuery

from core.tg.keyboards import MenuKeyboard
from core.tg.message_texts import Messages

router = Router(name='wb_actions')


@router.callback_query(F.data == 'wildberries')
async def choose_wb_actions(call: CallbackQuery) -> None:
    await call.message.edit_text(Messages.CHOSE_ACTION, reply_markup=MenuKeyboard())
    await call.answer()
