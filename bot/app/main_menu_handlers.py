from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart

from aiogram.fsm.context import FSMContext

from .auth_handlers import auth_start
from .api.users import user_exists

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
        await auth_start(msg, state)
        return

    await msg.answer(
        "Добро пожаловать в <b>Homie!</b> Здесь вы сможете найти или продать жильё в своём городе",
        parse_mode="HTML"
    )
    await main_menu(msg, state)

@router.message(F.text == "В главное меню")
async def main_menu(msg: Message, state: FSMContext):
    await state.clear()
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Найти жильё")],
            [KeyboardButton(text="Мои объявления")],
            [KeyboardButton(text="Мой профиль")],
        ],
        resize_keyboard=True
    )

    await msg.answer(
        "Вы в главном меню",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
