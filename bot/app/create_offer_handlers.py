from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from .util.offer import show_offer
from .util.auth import show_unauthorized
from .util.shared import is_int, handle_media_upload
from .keyboards import skip_keyboard

from .api.users import get_user_by_id
from .api.offers import get_user_offers, create_offer, get_offer_by_id, HouseOfferCreate

from .states import OfferCreate, Auth

router = Router()

@router.callback_query(F.data.startswith("show_offer:"))
async def show_house_offer(callback: CallbackQuery):
    await callback.answer()

    offer_id = int(callback.data.split(':')[1])
    offer = await get_offer_by_id(offer_id)

    visible_data = HouseOfferCreate(
        title=offer.title,
        description=offer.description,
        city=offer.city,
        district=offer.district,
        price=offer.price,
        media_files=offer.media_files
    )

    await show_offer(callback.message, visible_data)

@router.callback_query(F.data == "create_offer")
async def create_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    user = await get_user_by_id(callback.from_user.id)
    if user is None:
        await show_unauthorized(callback.message, state)
        await state.set_state(Auth.ask_to_auth)
        return
    
    await state.update_data(user=user.__dict__)

    # Клавиатура с подсказкой
    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=user.city)]], resize_keyboard=True)
    await callback.message.answer("В каком городе находится ваша недвижимость?", reply_markup=keyboard)

    await state.set_state(OfferCreate.city)

@router.message(OfferCreate.city)
async def select_city(msg: Message, state: FSMContext):
    if not msg.text:
        await msg.answer("Пожалуйста, введите название города")
        return
    
    await state.update_data(city=msg.text)
    await msg.answer("Где находится объект? Укажите район, улицу или название СНТ/деревни", reply_markup=skip_keyboard)
    await state.set_state(OfferCreate.district)

@router.message(OfferCreate.district)
async def enter_district(msg: Message, state: FSMContext):
    if msg.text != "Пропустить":
        await state.update_data(district=msg.text)
        
    txt = "Пожалуйста, дайте короткое название вашему объявлению\n\n<i>Пример:</i> Уютная комната в общежитии в центре"
    await msg.answer(txt, parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
    await state.set_state(OfferCreate.title)

@router.message(OfferCreate.title)
async def enter_title(msg: Message, state: FSMContext):
    if not msg.text:
        await msg.answer("Нужно написать название")
        return
    
    await state.update_data(title=msg.text)

    txt = "Укажите, сколько рублей в месяц стоит аренда вашей недвижимости. Этот этап можно пропустить"
    await msg.answer(txt, reply_markup=skip_keyboard)
    await state.set_state(OfferCreate.price)

@router.message(OfferCreate.price)
async def enter_price(msg: Message, state: FSMContext):
    if msg.text != "Пропустить":
        price_str = msg.text.replace(' ', '') # Удаление пробелов
        if not is_int(price_str):
            await msg.answer("Укажите целое число")
            return
        await state.update_data(price=price_str)

    txt = "Напишите подробное описание вашего объявления. Так Вы повысите вероятность найти арендатора"
    await msg.answer(txt, reply_markup=skip_keyboard)
    await state.set_state(OfferCreate.description)

@router.message(OfferCreate.description)
async def enter_descr(msg: Message, state: FSMContext):
    if not msg.text:
        await msg.answer("Нужно ввести текст")
        return
    if msg.text != "Пропустить":
        await state.update_data(descr=msg.text)
    
    await msg.answer("Теперь нужно отправить фотографии вашей недвижимости. Чем больше — тем лучше", reply_markup=ReplyKeyboardRemove())
    await state.set_state(OfferCreate.media)

@router.message(OfferCreate.media, F.text == "Завершить")
async def finalize_create_offer(msg: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    offer = HouseOfferCreate(
        owner_id=msg.from_user.id,
        title=data["title"],
        description=data.get("descr", ""),
        city=data["city"],
        district=data.get("district", ""),
        price=int(data.get("price", 0)),
        media_files=data["media_files"]
    )

    await create_offer(offer)

    await show_offer(msg, offer)

    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="В главное меню")]], resize_keyboard=True)
    msg_text = f"<b>Готово!</b> Вы успешно создали объявление о сдаче вашей недвижимости. Для более детального взаимодействия с вашими объявлениями ищите вкладку <b>Мои объявления</b> в главном меню."
    await msg.answer(msg_text, parse_mode="HTML", reply_markup=keyboard)

@router.message(OfferCreate.media)
async def upload_media(msg: Message, state: FSMContext):
    done = await handle_media_upload(msg, state, 10)
    if done:
        await finalize_create_offer(msg, state)

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