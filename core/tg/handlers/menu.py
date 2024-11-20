from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from core.schemas.user import User
from core.services.subscription import SubscriptionService
from core.services.user import UserService
from core.tg.keyboards import MenuKeyboard, MenuKeyboardWEmptySubs
from core.tg.message_texts import Messages
from core.tg.notifier_state import NotifierState

router = Router(name='menu')


@router.callback_query(NotifierState.waiting_action_w_product_for_exist, F.data == 'menu')
async def menu(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_reply_markup(reply_markup=MenuKeyboard())
    await state.clear()


@router.message(F.text == '/menu')
async def menu_command(
    message: Message, state: FSMContext, user_service: UserService, sub_service: SubscriptionService
) -> None:
    user = User(ID=state.key.user_id, ChatID=state.key.chat_id, TZOffset=-180)
    #   create user if not exist
    await user_service.create_user(user)

    subs_cnt: int = await sub_service.sub_cnt_by_user(user.id)
    if not subs_cnt:
        await message.answer(Messages.CHOSE_ACTION, reply_markup=MenuKeyboardWEmptySubs())
        return

    await message.answer(Messages.CHOSE_ACTION, reply_markup=MenuKeyboard())


@router.callback_query(NotifierState.waiting_product_id_for_del_subscribe, F.data == 'menu')
@router.callback_query(NotifierState.waiting_product_id, F.data == 'menu')
async def menu_from_choosing_product(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_text(Messages.CHOSE_ACTION, reply_markup=MenuKeyboard())
    await state.clear()
