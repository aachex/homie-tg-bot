import os

from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart, StateFilter

from aiogram.fsm.context import FSMContext

from ..states import MainMenu, SearchOffers, Offer

router = Router()

ADMIN_IDS = [int(admin_id) for admin_id in os.getenv("ADMIN_IDS").split(',')]

LOGO_FILE_ID = os.getenv("LOGO_FILE_ID")

@router.message(CommandStart())
@router.message(~StateFilter(SearchOffers.choice, Offer.view_likes), F.text == "Главное меню")
async def main_menu(msg: Message, state: FSMContext):
    await state.clear()
    await state.set_state(MainMenu.main_menu)

    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🏡 Найти жильё")],
        [KeyboardButton(text="Мой профиль")],
        [KeyboardButton(text="Мои объявления")],
    ], resize_keyboard=True)

    if msg.from_user.id in ADMIN_IDS:
        kb.keyboard.append([KeyboardButton(text="Админ-панель", style="primary")])

    msg_text = (
        "🏠 <b>Homie</b>\n"
        "<blockquote>ИИ-ассистент для поиска жилья</blockquote>\n\n"
        "Главное меню:\n"
        "🔍 <b>Найти жильё</b> — подбор квартир и домов\n"
        "👤 <b>Профиль</b> — ваша анкета для владельцев\n"
        "📋 <b>Мои объявления</b> — ваши предложения\n"
    )
    await msg.answer_photo(
        photo=LOGO_FILE_ID,
        caption=msg_text,
        reply_markup=kb,
        parse_mode="HTML"
    )
