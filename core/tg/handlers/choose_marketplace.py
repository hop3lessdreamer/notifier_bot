from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup

from core.tg.buttons import AVAILABLE_MARKET_PLACES
from core.tg.message_texts import Messages

router = Router(name='re_choose_mp_router')


@router.callback_query(F.data == 'choose_marketplace')
async def choose_mp(call: CallbackQuery) -> None:
    await call.message.edit_text(
        Messages.CHOSE_MARKET_PLACE,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[list(AVAILABLE_MARKET_PLACES)]),
    )
