from decimal import Decimal

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.media_group import MediaGroupBuilder

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from .util import is_decimal, handle_media_upload, normalize_decimal
from .keyboards import skipKeyboard

from .api.offers import get_user_offers, HouseOfferCreate

router = Router()

class CreateOffer(StatesGroup):
    type = State()
    city = State()
    title = State()
    price = State()
    description = State()
    media = State()  

@router.message(F.text == "Мои объявления")
async def my_offers(msg: Message):
    offers = await get_user_offers(msg.from_user.id)

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Создать объявление", callback_data="create_offer", style="primary"))

    for offer in offers:
        btn = InlineKeyboardButton(text=offer.title, callback_data=f"show_offer:{offer.id}")
        if offer.is_active:
            btn.style = "success"
        keyboard.add(btn)

    markup = keyboard.adjust(1).as_markup()
    markup.resize_keyboard = True
    await msg.answer(
        "Ниже представлены ваши объявления.\nАктивные отмечены 🟢зелёным цветом и находятся в начале списка",
        reply_markup=markup)
    
@router.callback_query(F.data.startswith("show_offer:"))
async def show_house_offer(msg: Message, data: HouseOfferCreate):
    """Отображает созданное объявление для подтверждения"""
    
    # ========== Форматирование цены ==========
    if data.price == 0:
        price_line = "💰 Цена: Не указана"
    else:
        # Форматируем число
        if data.price == data.price.to_integral():
            price_str = f"{int(data.price):,}".replace(',', ' ')
        else:
            price_str = f"{data.price:,.2f}".replace(',', ' ')
        
        # Добавляем суффикс
        suffix = "₽/месяц" if data.type == "RENT" else "₽"
        price_line = f"💰 Цена: {price_str} {suffix}"
    
    # ========== Тип объявления ==========
    if data.type == "RENT":
        type_text = "🏠 Сдаётся"
    elif data.type == "SELL":
        type_text = "💰 Продаётся"
    else:
        type_text = "📋 Объявление"
    
    # ========== Текстовое сообщение ==========
    message_text = f"""
<b>📋 {type_text}</b>

<b>🏷️ Название:</b> {data.title}
<b>📍 Город:</b> {data.city}
{price_line}

<b>📝 Описание:</b>
{data.description if data.description else '<i>—</i>'}

<b>📸 Фотографий:</b> {len(data.media_files)}
"""
    
    # ========== Отправка фотографий ==========
    if data.media_files:
        # Telegram ограничивает медиагруппу 10 элементами
        photos_to_send = data.media_files[:10]
        
        media_group = MediaGroupBuilder(caption=f"{message_text}")
        for photo_id in photos_to_send:
            media_group.add_photo(media=photo_id, parse_mode="HTML")
        
        await msg.answer_media_group(media=media_group.build())
        
        if len(data.media_files) > 10:
            await msg.answer(f"⚠️ Показаны первые 10 из {len(data.media_files)} фотографий")

@router.callback_query(F.data == "create_offer")
async def create_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Сдавать"), KeyboardButton(text="Продавать")]
    ], resize_keyboard=True)
    await callback.message.answer("Итак, вы решили создать объявление. Вы будете сдавать или продавать вашу недвижимость?", reply_markup=keyboard)
    await state.set_state(CreateOffer.type)

@router.message(CreateOffer.type)
async def select_type(msg: Message, state: FSMContext):
    if msg.text == "Сдавать":
        await state.update_data(type="RENT")
    elif msg.text == "Продавать":
        await state.update_data(type="SELL")
    else:
        await msg.answer("Неизвестный вариант")
        return
    
    # Достаём город пользователя для создания клавиатуры с подсказкой
    data = await state.get_data()
    city = data["user"]["city"]
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=city)]], resize_keyboard=True)

    await msg.answer("В каком городе находится ваша недвижимость?", reply_markup=keyboard)

    await state.set_state(CreateOffer.city)

@router.message(CreateOffer.city)
async def select_city(msg: Message, state: FSMContext):
    if not msg.text:
        await msg.answer("Пожалуйста, введите название города")
        return
    
    await state.update_data(city=msg.text)
    await msg.answer("Дайте краткое название вашему объявлению", reply_markup=ReplyKeyboardRemove())
    await state.set_state(CreateOffer.title)

@router.message(CreateOffer.title)
async def enter_title(msg: Message, state: FSMContext):
    if not msg.text:
        await msg.answer("Нужно написать название")
        return
    
    await state.update_data(title=msg.text)
    
    data = await state.get_data()
    offer_type = data["type"]

    msg_text = "Укажите, сколько рублей в месяц стоит аренда вашей недвижимости"
    if offer_type == "SELL":
        msg_text = "Укажите, сколько рублей стоит ваша недвижимость. Этот этап можно пропустить"

    await msg.answer(msg_text, reply_markup=skipKeyboard)
    await state.set_state(CreateOffer.price)

@router.message(CreateOffer.price)
async def enter_price(msg: Message, state: FSMContext):
    if msg.text == "Пропустить":
        await state.update_data(price=0)
    else:
        price_str = normalize_decimal(msg.text)
        if not is_decimal(price_str):
            await msg.answer("Укажите число, можно как целое, так и дробное (с разделением через точку или запятую)")
            return
        await state.update_data(price=price_str)
    
    data = await state.get_data()
    offer_type = data["type"]

    msg_text = "Напишите подробное описание вашего объявления. Так Вы повысите вероятность найти арендатора"
    if offer_type == "SELL":
        msg_text = "Напишите подробное описание вашего объявления. Так Вы повысите вероятность найти покупателя"

    await msg.answer(msg_text, reply_markup=skipKeyboard)
    await state.set_state(CreateOffer.description)

@router.message(CreateOffer.description)
async def enter_descr(msg: Message, state: FSMContext):
    if not msg.text:
        await msg.answer("Нужно ввести текст")
        return
    if msg.text != "Пропустить":
        await state.update_data(descr=msg.text)
    
    await msg.answer("Теперь нужно отправить фотографии вашей недвижимости. Чем больше — тем лучше", reply_markup=ReplyKeyboardRemove())
    await state.set_state(CreateOffer.media)

@router.message(CreateOffer.media, F.text == "Завершить")
async def finalize_create_offer(msg: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    offer = HouseOfferCreate(
        title=data["title"],
        description=data.get("descr", ""),
        city=data["city"],
        price=Decimal(data["price"]),
        type=data["type"],
        media_files=data["media_files"]
    )

    await show_house_offer(msg, offer)

@router.message(CreateOffer.media)
async def enter_descr(msg: Message, state: FSMContext):
    done = await handle_media_upload(msg, state, 10)
    if done:
        await finalize_create_offer()
