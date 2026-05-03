from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from aiogram.fsm.context import FSMContext

from ..api.users import get_user_by_id
from ..api.offers import get_rand_offer

from ..util.offer import show_offer
from ..util.shared import normalize_city

from .main_menu import main_menu as show_main_menu

from ..states import SearchOffers, MainMenu

router = Router()

@router.message(MainMenu.main_menu, F.text == "🏡 Найти квартиру/дом")
@router.message(SearchOffers.offer_not_found, F.text == "Указать город повторно")
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
    await state.update_data(city=normalize_city(msg.text))

    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="❤️"), KeyboardButton(text="👎")],
        [KeyboardButton(text="Вернуться в главное меню")]
    ], resize_keyboard=True)
    
    await msg.answer("🔎", reply_markup=kb)
    await state.set_state(SearchOffers.choice)
    await show_next_offer(msg, state)

async def show_next_offer(msg: Message, state: FSMContext):
    data = await state.get_data()
    city = data["city"]
    offer = await get_rand_offer(msg.from_user.id, city)
    if offer is None:
        await state.set_state(SearchOffers.offer_not_found)
        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Указать город повторно")],
            [KeyboardButton(text="В главное меню")],
        ], resize_keyboard=True)

        await msg.answer("Мы не нашли ни одного объявления в указанном городе. Возможно опечатка?", reply_markup=kb)
        return

    await show_offer(msg, offer)

@router.message(SearchOffers.choice)
async def evaluate_offer(msg: Message, state: FSMContext):
    if msg.text == "👎":
        await show_next_offer(msg, state)
    elif msg.text == "❤️":
        # TODO: send like to db
        await show_next_offer(msg, state)
    elif msg.text == "Вернуться в главное меню":
        await show_main_menu(msg, state)
    else:
        await msg.answer("Поставьте ❤️ или 👎 этому объявлению")