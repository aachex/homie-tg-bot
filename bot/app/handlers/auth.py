from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

from aiogram.fsm.context import FSMContext
from aiogram import flags

from ..keyboards import skip_keyboard, evaluate_keyboard

from .main_menu import main_menu as show_main_menu
from .search_offers import show_next_offer

from ..util.auth import show_profile, show_unauthorized
from ..util.shared import is_int, handle_media_upload, normalize_city
from ..api.users import get_user_by_id, create_user, edit_user, User, UserVisibleData

from ..states import Auth, MainMenu, SearchOffers

router = Router()

@flags.rate_limit(rate=1, key="user")
@router.message(MainMenu.main_menu, F.text == "Мой профиль")
async def my_profile(msg: Message, state: FSMContext):
    user = await get_user_by_id(msg.from_user.id)
    if user is None:
        await show_unauthorized(msg)
        return

    await state.clear()
    await state.update_data(user=user.__dict__)

    profile_data = UserVisibleData(
        name=user.name,
        age=user.age,
        city=user.city,
        description=user.description,
        media_files=user.media_files
    )
    await show_profile_with_restart_keyboard(msg, state, profile_data)

@router.callback_query(F.data.startswith("authorize:"))
async def auth_start_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=callback.from_user.first_name)]], resize_keyboard=True)

    data = await state.get_data()
    if "user" in data:
        kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=data["user"]["name"])]], resize_keyboard=True)

    await callback.message.answer("Пожалуйста, введите Ваше имя", reply_markup=kb)
    await state.set_state(Auth.name)

    offer_id_str = callback.data.split(':')[1]
    if offer_id_str != '0':
        offer_id = int(offer_id_str)
        await state.update_data(offer_id=offer_id)
    
@flags.rate_limit(rate=1, key="user")
@router.message(MainMenu.profile, F.text == "Заполнить профиль заново")
async def auth_start_msg(msg: Message, state: FSMContext):
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=msg.from_user.first_name)]], resize_keyboard=True)

    data = await state.get_data()
    if "user" in data:
        kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=data["user"]["name"])]], resize_keyboard=True)

    await msg.answer("Пожалуйста, введите Ваше имя", reply_markup=kb)
    await state.set_state(Auth.name)

@flags.rate_limit(rate=1, key="user")
@router.message(Auth.name)
async def auth_name(msg: Message, state: FSMContext):
    maxNameLen = 100
    if len(msg.text) > maxNameLen:
        await msg.answer(f"Име не может быть длиннее {maxNameLen} символов")
        return
    
    data = await state.get_data()
    kb = ReplyKeyboardRemove()
    if "user" in data:
        kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=str(data["user"]["age"]))]], resize_keyboard=True)

    await state.update_data(name=msg.text)
    await msg.answer("Сколько Вам лет?", reply_markup=kb)
    await state.set_state(Auth.age)

@flags.rate_limit(rate=1, key="user")
@router.message(Auth.age)
async def auth_age(msg: Message, state: FSMContext):
    if not is_int(msg.text):
        await msg.answer("Возраст должен быть числом")
        return
    if int(msg.text) < 0 or int(msg.text) > 150:
        await msg.answer("Возраст должен быть от 0 до 150 включительно")
        return
    
    data = await state.get_data()
    kb = ReplyKeyboardRemove()
    if "user" in data:
        kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=data["user"]["city"])]], resize_keyboard=True)

    await state.update_data(age=msg.text)
    await msg.answer("Из какого вы города?", reply_markup=kb)
    await state.set_state(Auth.city)

@flags.rate_limit(rate=1, key="user")
@router.message(Auth.city)
async def auth_city(msg: Message, state: FSMContext):
    data = await state.get_data()
    kb = skip_keyboard
    if "user" in data:
        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Пропустить")],
            [KeyboardButton(text="Оставить текущее описание")],
        ], resize_keyboard=True)

    await state.update_data(city=normalize_city(msg.text))
    await msg.answer("Расскажите немного о себе. Данный пункт необязателен, но желателен", reply_markup=kb)
    await state.set_state(Auth.descr)

@flags.rate_limit(rate=1, key="user")
@router.message(Auth.descr)
async def auth_descr(msg: Message, state: FSMContext):
    data = await state.get_data()

    if not msg.text:
        await msg.answer("Нужно ввести текст")
        return
    if msg.text == "Оставить текущее описание":
        await state.update_data(descr=data["user"]["description"])
    elif msg.text != "Пропустить":
        await state.update_data(descr=msg.text)

    kb = ReplyKeyboardRemove()
    if "user" in data:
        kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Оставить текущие фотографии")]], resize_keyboard=True)
    await msg.answer("Пожалуйста, отправьте фотографию с вашим лицом. Профилям без лица меньше доверяют", reply_markup=kb)
    await state.set_state(Auth.media_files)

@flags.rate_limit(rate=1, key="user")
@router.message(Auth.media_files, F.text == "Завершить")
async def finalize_auth(msg: Message, state: FSMContext):
    data = await state.get_data()
    if "media_files" not in data:
        return
    
    await state.clear()

    user = UserVisibleData(
        name=data["name"],
        age=int(data["age"]),
        city=data["city"],
        description=data.get("descr", ""),
        media_files=data["media_files"]
    )

    if "user" in data:
        # Если в fsm есть старые данные пользователя, то значит он 
        # уже регистрировался и нужно редактировать его профиль, а не создавать
        await edit_user(msg.from_user.id, user)
    else:
        new_user = User(
            id=msg.from_user.id,
            name=user.name,
            age=user.age,
            city=user.city,
            description=user.description,
            media_files=user.media_files,
        )
        await create_user(new_user)
        
    if "offer_id" in data:
        await state.update_data(offer_id=int(data["offer_id"]))

    await state.update_data(user=user.__dict__)
    await show_profile_with_restart_keyboard(msg, state, user)

@flags.rate_limit(rate=1, key="user")
@router.message(Auth.media_files)
async def auth_media(msg: Message, state: FSMContext):
    data = await state.get_data()
    if msg.text == "Оставить текущие фотографии" and "user" in data:
        # Если пользователь решил оставить фото и у нас есть информация о его старых фото
        await state.update_data(media_files=data["user"]["media_files"])
        await finalize_auth(msg, state)
        return
    
    done = await handle_media_upload(msg, state, 3)
    if done:
        await finalize_auth(msg, state)

async def show_profile_with_restart_keyboard(msg: Message, state: FSMContext, user: UserVisibleData):
    await state.set_state(MainMenu.profile)
    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Заполнить профиль заново")],
        [KeyboardButton(text="Готово")],
    ], resize_keyboard=True)
    await msg.answer("Так выглядит ваш профиль:", reply_markup=keyboard)
    await show_profile(msg, user)

@router.message(MainMenu.profile, F.text == "Готово")
async def profile_done(msg: Message, state: FSMContext):
    data = await state.get_data()
    if "offer_id" not in data:
        await show_main_menu(msg, state)
        return
    
    await state.set_state(SearchOffers.choice)
    await state.update_data(user_id=msg.from_user.id)
    
    offer_id = int(data["offer_id"])
    await msg.answer("🔎", reply_markup=evaluate_keyboard)
    await show_next_offer(msg, state, offer_id)
