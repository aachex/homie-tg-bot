from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import CommandStart, StateFilter

from aiogram.fsm.context import FSMContext

from ..keyboards import main_menu_keyboard

from ..states import MainMenu, SearchOffers

router = Router()

@router.message(CommandStart())
async def start(msg: Message, state: FSMContext):
    await state.clear()

    await msg.answer(
        "Добро пожаловать в <b>Homie!</b> Здесь вы сможете найти или продать жильё в своём городе",
        parse_mode="HTML"
    )
    await main_menu(msg, state)

@router.message(~StateFilter(SearchOffers.choice), F.text == "В главное меню")
async def main_menu(msg: Message, state: FSMContext):
    await state.clear()
    await state.set_state(MainMenu.main_menu)

    await msg.answer(
        "Вы в главном меню",
        reply_markup=main_menu_keyboard,
        parse_mode="HTML"
    )
