from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from .main_menu import ADMIN_IDS

from ..states import MainMenu, Admin

router = Router()

@router.message(MainMenu.main_menu, F.from_user.id.in_(ADMIN_IDS), F.text == "Админ-панель")
async def admin_panel(msg: Message, state: FSMContext):
    await state.set_state(Admin.panel)

    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="⚠️ Жалобы")],
        [KeyboardButton(text="Главное меню")]
    ], resize_keyboard=True)
    await msg.answer("👑 Добро пожаловать в панель администраторов", parse_mode="HTML", reply_markup=kb)
