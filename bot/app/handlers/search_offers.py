from dataclasses import asdict

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton

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

from ..keyboards import back_to_main_menu_keyboard

router = Router()

@router.message(MainMenu.main_menu, F.text == "🏡 Найти жильё")
async def search_start(msg: Message, state: FSMContext):
    await state.clear()

    user = await get_user_by_id(msg.from_user.id)

    if not user:  # Если юзер не заполнял профиль, то просим его указать город явно
        await msg.answer("В каком городе искать объявления?", reply_markup=ReplyKeyboardRemove())
        await state.set_state(SearchOffers.city)
        return

    await state.update_data(user=asdict(user))
    await state.update_data(city=user.city)

    today_likes = await get_today_likes(msg.from_user.id)
    if not today_likes:
        await show_server_error(msg)
        return

    await state.update_data(today_likes_count=today_likes.likes_count)
    await state.update_data(max_likes_count=today_likes.max_likes)

    await send_mag(msg)
    await show_next_offer(msg, state)
    

@router.message(SearchOffers.city)
async def select_city(msg: Message, state: FSMContext):
    if not msg.text:
        await msg.answer("Укажите город")
        return
    city = normalize_city(msg.text)
    await state.update_data(city=city)

    # Проверка что в указанном городе есть объявления
    offer = await get_rand_offer(msg.from_user.id, city, None)
    if not offer:
        await msg.answer("🔎")
        await msg.answer(
            "Мы не нашли ни одного объявления в указанном городе. Введите название ещё раз",
            reply_markup=back_to_main_menu_keyboard
        )
        return
    
    await send_mag(msg)
    await show_next_offer(msg, state)

async def show_next_offer(msg: Message, state: FSMContext, offer_id: int = 0, relevance: int = 0):
    if offer_id != 0 and relevance == 0:
        raise Exception("relevance == 0 when offer_id != 0")

    data = await state.get_data()

    flags = UserFlags(**data["user"]["flags"]) if "flags" in data.get("user", {}) else None

    city = data["city"]
    
    if offer_id != 0:
        offer = await get_offer_by_id(offer_id)
        if offer is None:
            await show_server_error(msg)
            return
    else:
        offer = await get_rand_offer(msg.from_user.id, city, flags)
        if offer is None:
            await msg.answer(
                "Вы просмотрели все доступные на сегодня предложения. Возвращайтесь позже!",
                reply_markup=back_to_main_menu_keyboard
            )
            return
        
        relevance = offer.relevance_percent
        offer = offer.offer

    await state.update_data(offer_id=offer.id)
    await state.update_data(offer_relevance=relevance)
    
    await show_offer(msg, offer, relevance)
    await state.set_state(SearchOffers.choice)

@router.message(SearchOffers.choice, F.text.in_({"❤️", "👎"}))
async def evaluate_offer(msg: Message, state: FSMContext):
    # Если поставили лайк - фиксируем в бд
    if msg.text == "❤️":
        data = await state.get_data()

        # Проверяем, не превысили ли дневной лимит лайков
        today_likes_count = int(data["today_likes_count"])
        max_likes_count = int(data["max_likes_count"])

        if today_likes_count >= max_likes_count:
            txt = (
                "<b>Слишком много ❤️ за сегодня</b>\n\n"
                "У премиум-пользователей ограничений нет. С помощью команды /premium Вы можете узнать подробности"
            )
            await msg.answer(
                text=txt,
                parse_mode="HTML", 
            )
            return

        # Проверяем что пользователь зарегистрирован
        if "user" not in data:
            await show_unauthorized(msg)
            return

        # Фиксируем лайк в бд
        like = AddLikeRequest(
            offer_id=int(data["offer_id"]),
            user_id=int(data["user"]["id"]),
            relevance=int(data["offer_relevance"])
        )
        await add_like_to_offer(like)
        await state.update_data(today_likes_count=today_likes_count+1)

    await show_next_offer(msg, state)

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
    # Показываем то же объявление, на которое юзер хотел пожаловаться
    data = await state.get_data()
    offer_id = int(data["offer_id"])
    relevance = int(data["offer_relevance"])

    await send_mag(msg)
    await show_next_offer(msg, state, offer_id, relevance)

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

async def show_server_error(msg: Message):
    await msg.answer(
        "Произошла непредвиденная ошибка на сервере. Попробуйте позже или сообщите в техподдержку: @homie_bot_support",
        reply_markup=back_to_main_menu_keyboard
    )
