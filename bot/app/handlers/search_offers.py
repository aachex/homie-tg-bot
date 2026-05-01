from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from aiogram.fsm.context import FSMContext

from ..api.offers import get_rand_offer
from ..util.offer import show_offer

from .main_menu import main_menu as show_main_menu

from ..states import SearchOffers

router = Router()

sent_magnifier: dict[int, bool] = {}

@router.message(F.text == "🏡 Найти квартиру/дом")
async def search_offers(msg: Message, state: FSMContext):
    await state.clear()

    if msg.chat.id not in sent_magnifier:
        sent_magnifier[msg.chat.id] = True

        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="❤️"), KeyboardButton(text="👎")],
            [KeyboardButton(text="Вернуться в главное меню")]
        ], resize_keyboard=True)
        await msg.answer("🔎", reply_markup=kb)

    offer = await get_rand_offer(msg.from_user.id)
    await show_offer(msg, offer)

    await state.set_state(SearchOffers.choice)

@router.message(SearchOffers.choice)
async def evaluate_offer(msg: Message, state: FSMContext):
    if msg.text == "👎":
        await search_offers(msg, state)
    elif msg.text == "❤️":
        # TODO: send like to db
        await search_offers(msg, state)
    elif msg.text == "Вернуться в главное меню":
        del sent_magnifier[msg.chat.id]
        await show_main_menu(msg, state)
    else:
        await msg.answer("Поставьте ❤️ или 👎 этому объявлению")