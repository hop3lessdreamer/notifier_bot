from typing import cast

from aiogram import F, Router
from aiogram.types import Message
from aiogram.types import User as TGUser

from core.schemas.user import User
from core.services.user import UserService
from core.tg.keyboards import MenuKeyboardWEmptySubs
from core.tg.message_texts import Messages

router = Router(name='start_bot_router')


@router.message(F.text == '/start')
async def start_message(message: Message, user_service: UserService) -> None:
    await message.answer(Messages.HELLO)
    await user_service.create_user(
        User(ID=cast(TGUser, message.from_user).id, ChatID=message.chat.id, TZOffset=-180)
    )
    await message.answer(Messages.CHOSE_ACTION, reply_markup=MenuKeyboardWEmptySubs())
