from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from aiogram.fsm.context import FSMContext

from .auth_handlers import auth_start
from .api.users import user_exists
from .util import show_main_menu

router = Router()

@router.message(CommandStart())
async def start(msg: Message, state: FSMContext):
    await state.clear()
    
    # Если пользователь не регистрировался, то просим его заполнить профиль перед началом
    if not await user_exists(msg.from_user.id):
        await msg.answer(
            "Добро пожаловать в <b>Homie!</b> Здесь вы сможете найти или продать жильё в своём городе.\n\nНо прежде чем начать, вам нужно создать профиль",
            parse_mode="HTML"
        )
        await state.update_data(new_user=True)
        await auth_start(msg, state)
        return

    await msg.answer(
        "Добро пожаловать в <b>Homie!</b> Здесь вы сможете найти или продать жильё в своём городе",
        parse_mode="HTML"
    )
    await show_main_menu(msg)

@router.message(F.text == "Вернуться в главное меню")
async def main_menu(msg: Message):
    await show_main_menu(msg)
