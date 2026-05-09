from dataclasses import asdict

from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from aiogram.fsm.context import FSMContext

from ..api.users import get_user_by_id
from ..api.offers import get_rand_offer, add_like_to_offer, get_offer_by_id

from ..util.offer import show_offer
from ..util.auth import show_unauthorized
from ..util.shared import normalize_city

from .main_menu import main_menu as show_main_menu

from ..states import SearchOffers, MainMenu
from ..model.ruleset import Ruleset

from ..keyboards import evaluate_keyboard

router = Router()

_user_city: dict[int, str] = {}

@router.message(MainMenu.main_menu, F.text == "🏡 Найти квартиру/дом")
@router.message(SearchOffers.offer_not_found, F.text == "Указать город повторно")
async def search_start(msg: Message, state: FSMContext):
    await state.clear()

    kb = ReplyKeyboardRemove()
    user = await get_user_by_id(msg.from_user.id)
    if user is not None:
        kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=user.city)]], resize_keyboard=True)
        await state.update_data(user=asdict(user))

    await msg.answer("Из какого города показывать объявления?", reply_markup=kb)
    await state.set_state(SearchOffers.city)

@router.message(SearchOffers.city)
async def select_city(msg: Message, state: FSMContext):
    if not msg.text:
        await msg.answer("Укажите город")
        return
    city = normalize_city(msg.text)
    _user_city[msg.from_user.id] = city

    # Проверка что в указанном городе есть объявления
    data = await state.get_data()

    ruleset = None
    if "user" in data:
        ruleset = Ruleset(**data["user"]["details"])
    offer = await get_rand_offer(msg.from_user.id, city, ruleset)
    if offer is None:
        await state.set_state(SearchOffers.offer_not_found)
        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Указать город повторно")],
            [KeyboardButton(text="Главное меню")],
        ], resize_keyboard=True)

        await msg.answer("🔎")
        await msg.answer("Мы не нашли ни одного объявления в указанном городе. Возможно опечатка?", reply_markup=kb)
        return
    
    await msg.answer("🔎", reply_markup=evaluate_keyboard)

    await state.set_state(SearchOffers.choice)
    await show_next_offer(msg, state)

async def show_next_offer(msg: Message, state: FSMContext, id: int = 0):
    offer = None
    user_id = msg.from_user.id
    
    if id == 0 and user_id in _user_city:
        data = await state.get_data()
        ruleset = None
        if "user" in data:
            ruleset = Ruleset(**data["user"]["details"])

        city = _user_city[user_id]
        
        offer = await get_rand_offer(msg.from_user.id, city, ruleset)
    elif id != 0:
        offer = await get_offer_by_id(id)
    
    if offer is None:
        await state.set_state(SearchOffers.offer_not_found)
        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Главное меню")],
        ], resize_keyboard=True)

        await msg.answer("Произошла непредвиденная ошибка... Извините", reply_markup=kb)
        return

    await state.update_data(offer_id=offer.id)
    await show_offer(msg, offer)

@router.message(SearchOffers.choice)
async def evaluate_offer(msg: Message, state: FSMContext):
    if msg.text == "Главное меню":
        user_id = msg.from_user.id
        if user_id in _user_city:
            del _user_city[user_id]
        await show_main_menu(msg, state)
        return
    
    if msg.text != "❤️" and msg.text != "👎":
        await msg.answer("Поставьте ❤️ или 👎 этому объявлению")
        return
    
    # Если поставили лайк - фиксируем в бд
    if msg.text == "❤️":
        data = await state.get_data()
        offer_id = int(data["offer_id"])

        # Проверяем что пользователь зарегистрирован
        if "user" not in data:
            await show_unauthorized(msg, offer_id)
            return
        
        user_id = int(data["user"]["id"])
        await add_like_to_offer(offer_id, user_id)
    
    await show_next_offer(msg, state)
        