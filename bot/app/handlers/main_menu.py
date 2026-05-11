import os

from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart, StateFilter

from aiogram.fsm.context import FSMContext

from ..states import MainMenu, SearchOffers, Offer

router = Router()

ADMIN_IDS = [int(admin_id) for admin_id in os.getenv("ADMIN_IDS").split(',')]

@router.message(CommandStart())
async def start(msg: Message, state: FSMContext):
    await state.clear()

    await msg.answer(
        "Добро пожаловать в <b>Homie!</b> Здесь вы сможете найти или продать жильё в своём городе",
        parse_mode="HTML"
    )
    await main_menu(msg, state)

@router.message(~StateFilter(SearchOffers.choice, Offer.view_likes), F.text == "Главное меню")
async def main_menu(msg: Message, state: FSMContext):
    await state.clear()
    await state.set_state(MainMenu.main_menu)

    kb_array = [
        [KeyboardButton(text="🏡 Найти квартиру/дом")],
        [KeyboardButton(text="Мой профиль")],
        [KeyboardButton(text="Мои объявления")],
    ]
    if msg.from_user.id in ADMIN_IDS:
        kb_array.append([KeyboardButton(text="Админ-панель", style="primary")])

    kb = ReplyKeyboardMarkup(keyboard=kb_array, resize_keyboard=True)

    await msg.answer(
        "Вы в главном меню",
        reply_markup=kb,
        parse_mode="HTML"
    )
