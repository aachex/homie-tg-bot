from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from .util import is_int, handle_media_upload, show_offer
from .keyboards import skip_keyboard

from .api.users import get_user_by_id
from .api.offers import get_user_offers, create_offer, get_offer_by_id, HouseOfferCreate

router = Router()

class CreateOffer(StatesGroup):
    type = State()
    city = State()
    title = State()
    price = State()
    description = State()
    media = State()

@router.message(F.text == "Мои объявления")
async def my_offers(msg: Message, state: FSMContext):
    await state.clear()

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
async def show_house_offer(callback: CallbackQuery):
    await callback.answer()

    offer_id = int(callback.data.split(':')[1])
    offer = await get_offer_by_id(offer_id)

    visible_data = HouseOfferCreate(
        title=offer.title,
        description=offer.description,
        city=offer.city,
        price=offer.price,
        type=offer.type,
        media_files=offer.media_files
    )

    await show_offer(callback.message, visible_data)

@router.callback_query(F.data == "create_offer")
async def create_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    user = await get_user_by_id(callback.from_user.id)
    await state.update_data(user=user.__dict__)

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
        msg_text = "Укажите, сколько рублей стоит ваша недвижимость"
    msg_text += ". Этот этап можно пропустить"

    await msg.answer(msg_text, reply_markup=skip_keyboard)
    await state.set_state(CreateOffer.price)

@router.message(CreateOffer.price)
async def enter_price(msg: Message, state: FSMContext):
    if msg.text == "Пропустить":
        await state.update_data(price=0)
    else:
        price_str = msg.text.replace(' ', '') # Удаление пробелов
        if not is_int(price_str):
            await msg.answer("Укажите целое число")
            return
        await state.update_data(price=price_str)
    
    data = await state.get_data()
    offer_type = data["type"]

    msg_text = "Напишите подробное описание вашего объявления. Так Вы повысите вероятность найти арендатора"
    if offer_type == "SELL":
        msg_text = "Напишите подробное описание вашего объявления. Так Вы повысите вероятность найти покупателя"

    await msg.answer(msg_text, reply_markup=skip_keyboard)
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
        owner_id=msg.from_user.id,
        title=data["title"],
        description=data.get("descr", ""),
        city=data["city"],
        price=int(data["price"]),
        type=data["type"],
        media_files=data["media_files"]
    )

    await create_offer(offer)

    await show_offer(msg, offer)

    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Вернуться в главное меню")]], resize_keyboard=True)
    t = "сдаче" if offer.type == "RENT" else "продаже"
    msg_text = f"<b>Готово!</b> Вы успешно создали объявление о {t} вашей недвижимости. Для более детального взаимодействия с вашими объявлениями ищите вкладку <b>Мои объявления</b> в главном меню."
    await msg.answer(msg_text, parse_mode="HTML", reply_markup=keyboard)

@router.message(CreateOffer.media)
async def enter_descr(msg: Message, state: FSMContext):
    done = await handle_media_upload(msg, state, 10)
    if done:
        await finalize_create_offer()
