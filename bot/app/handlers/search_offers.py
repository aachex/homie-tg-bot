from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from aiogram.fsm.context import FSMContext

from ..api.users import get_user_by_id
from ..api.offers import get_rand_offer
from ..util.offer import show_offer

from .main_menu import main_menu as show_main_menu

from ..states import SearchOffers, MainMenu

router = Router()

@router.message(MainMenu.main_menu, F.text == "🏡 Найти квартиру/дом")
async def search_start(msg: Message, state: FSMContext):
    await state.clear()

    kb = ReplyKeyboardRemove()
    user = await get_user_by_id(msg.from_user.id)
    if user is not None:
        kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=user.city)]], resize_keyboard=True)
    await msg.answer("Из какого города показывать объявления?", reply_markup=kb)
    await state.set_state(SearchOffers.city)

@router.message(SearchOffers.city)
async def select_city(msg: Message, state: FSMContext):
    if not msg.text:
        await msg.answer("Укажите город")
        return
    await state.update_data(city=msg.text)
    await state.set_state(SearchOffers.show_first_offer)
    await search_offers(msg, state)

@router.message(SearchOffers.show_first_offer)
async def search_offers(msg: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == "SearchOffers:show_first_offer":
        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="❤️"), KeyboardButton(text="👎")],
            [KeyboardButton(text="Вернуться в главное меню")]
        ], resize_keyboard=True)
        await msg.answer("🔎", reply_markup=kb)

    data = await state.get_data()
    city = data["city"]
    offer = await get_rand_offer(msg.from_user.id, city)
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
        await show_main_menu(msg, state)
    else:
        await msg.answer("Поставьте ❤️ или 👎 этому объявлению")