from dataclasses import asdict

from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.fsm.context import FSMContext

from ..api.users import get_user_by_id, get_today_likes
from ..api.offers import get_rand_offer, add_like_to_offer, get_offer_by_id
from ..api.reports import create_report

from ..util.offer import show_offer
from ..util.auth import show_unauthorized
from ..util.shared import normalize_city

from .main_menu import main_menu as show_main_menu

from ..states import SearchOffers, MainMenu
from ..model.report import ReportCreate
from ..model.user import UserFlags
from ..model.house_offer import AddLikeRequest

from ..keyboards import evaluate_keyboard

router = Router()

_user_city: dict[int, str] = {}

@router.message(MainMenu.main_menu, F.text == "🏡 Найти жильё")
@router.message(SearchOffers.offer_not_found, F.text == "Указать город повторно")
async def search_start(msg: Message, state: FSMContext):
    await state.clear()

    kb = ReplyKeyboardRemove()
    user = await get_user_by_id(msg.from_user.id)
    if user is not None:
        kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=user.city)]], resize_keyboard=True)
        await state.update_data(user=asdict(user))

    today_likes = await get_today_likes(msg.from_user.id)
    if not today_likes:
        await msg.answer("Произошла непредвиденная ошибка на сервере. Попробуйте позже или сообщите в техподдержку: @homie_bot_support")
        return

    await state.update_data(today_likes_count=today_likes.likes_count)
    await state.update_data(max_likes_count=today_likes.max_likes)

    await msg.answer("Из какого города показывать объявления?", reply_markup=kb)
    await state.set_state(SearchOffers.city)

@router.message(SearchOffers.city)
async def select_city(msg: Message, state: FSMContext):
    if not msg.text:
        await msg.answer("Укажите город")
        return
    city = normalize_city(msg.text)
    await state.update_data(city=city)

    # Проверка что в указанном городе есть объявления
    data = await state.get_data()

    flags = None
    if "user" in data and "flags" in data["user"]:
        flags = UserFlags(**data["user"]["flags"])
    offer = await get_rand_offer(msg.from_user.id, city, flags)
    if offer is None:
        await state.set_state(SearchOffers.offer_not_found)
        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Указать город повторно")],
            [KeyboardButton(text="Главное меню")],
        ], resize_keyboard=True)

        await msg.answer("🔎")
        await msg.answer("Мы не нашли ни одного объявления в указанном городе. Возможно опечатка?", reply_markup=kb)
        return
    
    await send_mag(msg)
    await show_next_offer(msg, state)

async def show_next_offer(msg: Message, state: FSMContext):
    data = await state.get_data()
    flags = None
    if "user" in data and "flags" in data["user"]:
        flags = UserFlags(**data["user"]["flags"])

    city = data["city"]
        
    offer = await get_rand_offer(msg.from_user.id, city, flags)
    if offer is None:
        await state.set_state(SearchOffers.offer_not_found)
        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Главное меню")],
        ], resize_keyboard=True)

        await msg.answer("Вы просмотрели все доступные на сегодня предложения. Возвращайтесь позже!", reply_markup=kb)
        return
    
    relevance = offer.relevance_percent
    offer = offer.offer

    await state.update_data(offer_id=offer.id)
    await state.update_data(offer_relevance=relevance)
    await show_offer(msg, offer, relevance)
    await state.set_state(SearchOffers.choice)

@router.message(SearchOffers.choice, F.text.in_({"❤️", "👎"}))
async def evaluate_offer(msg: Message, state: FSMContext):    
    if msg.text != "❤️" and msg.text != "👎":
        await msg.answer("Поставьте ❤️ или 👎 этому объявлению")
        return
    
    # Если поставили лайк - фиксируем в бд
    if msg.text == "❤️":
        data = await state.get_data()
        today_likes_count = int(data.get("today_likes_count"))
        max_likes_count = int(data["max_likes_count"])

        if today_likes_count >= max_likes_count:
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🌟 Премиум", callback_data="buy_premium")]
            ])
            txt = "<b>Слишком много ❤️ за сегодня</b>\n\nОформите премиум, чтобы лайкать без ограничений и быстрее найти подходящее предложение"
            await msg.answer(
                text=txt,
                parse_mode="HTML",
                reply_markup=kb,   
            )
            return

        # Проверяем что пользователь зарегистрирован
        if "user" not in data:
            await show_unauthorized(msg)
            return
        
        offer_id = int(data["offer_id"])
        user_id = int(data["user"]["id"])
        relevance = int(data["offer_relevance"])
        
        like = AddLikeRequest(
            offer_id=offer_id,
            user_id=user_id,
            relevance=relevance
        )
        await add_like_to_offer(like)
    
    await show_next_offer(msg, state)

@router.message(SearchOffers.choice, F.text == "Главное меню")
async def main_menu(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    if user_id in _user_city:
        del _user_city[user_id]
    await show_main_menu(msg, state)

@router.message(SearchOffers.choice, F.text == "⚠️ Жалоба")
async def handle_report(msg: Message, state: FSMContext):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📢 Спам / реклама")],
            [KeyboardButton(text="💰 Мошенничество / обман")],
            [KeyboardButton(text="❌ Неверная информация")],
            [KeyboardButton(text="🔞 Неподобающий контент")],
            [KeyboardButton(text="Отмена")],
        ],
        resize_keyboard=True
    )
    await msg.answer(
        "📋 <b>Пожаловаться на объявление</b>\n\n"
        "Выберите причину жалобы или напишите свой вариант:",
        reply_markup=kb,
        parse_mode="HTML"
    )

    await state.set_state(SearchOffers.report_reason)

@router.message(SearchOffers.report_reason, F.text == "Отмена")
async def cancel_report(msg: Message, state: FSMContext):
    data = await state.get_data()
    offer_id = int(data["offer_id"])
    await send_mag(msg)
    await show_next_offer(msg, state, offer_id)

@router.message(SearchOffers.report_reason)
async def report_reason(msg: Message, state: FSMContext):
    if not msg.text:
        await msg.answer("Напишите причину жалобы")
        return
    reason = msg.text

    data = await state.get_data()
    offer_id = int(data["offer_id"])

    report = ReportCreate(
        offer_id=offer_id,
        reporter_id=msg.from_user.id,
        reason=reason
    )
    await create_report(report)
    await msg.answer("Жалоба отправлена. Модераторы её рассмотрят в ближайшее время")

    await send_mag(msg)
    await show_next_offer(msg, state)

async def send_mag(msg: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❤️"), KeyboardButton(text="👎")],
            [KeyboardButton(text="⚠️ Жалоба")],
            [KeyboardButton(text="Главное меню")]
        ], resize_keyboard=True
    )

    await msg.answer("🔎", reply_markup=kb)