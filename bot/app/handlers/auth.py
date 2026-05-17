import os
from dataclasses import asdict

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

from aiogram.fsm.context import FSMContext

from ..keyboards import skip_keyboard, evaluate_keyboard, yes_no_keyboard

from .main_menu import main_menu as show_main_menu
from .search_offers import show_next_offer, send_mag

from ..util.auth import show_profile, show_unauthorized
from ..util.shared import is_int, handle_media_upload, normalize_city
from ..api.users import get_user_by_id, create_user, edit_user, User, UserVisibleData

from ..model.ruleset import Ruleset

from ..states import Auth, MainMenu, SearchOffers

router = Router()

@router.message(MainMenu.main_menu, F.text == "Мой профиль")
async def my_profile(msg: Message, state: FSMContext):
    user = await get_user_by_id(msg.from_user.id)
    if user is None:
        await show_unauthorized(msg)
        return

    await state.clear()
    await state.update_data(user=asdict(user))

    profile_data = UserVisibleData(
        name=user.name,
        age=user.age,
        city=user.city,
        description=user.description,
        media_files=user.media_files,
        details=user.details
    )
    await show_profile_with_restart_keyboard(msg, state, profile_data)

async def auth_start(msg: Message, state: FSMContext, first_name: str):
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=first_name)]], resize_keyboard=True)

    data = await state.get_data()
    if "user" in data:
        kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=data["user"]["name"])]], resize_keyboard=True)

    await msg.answer("Пожалуйста, введите Ваше имя", reply_markup=kb)
    await state.set_state(Auth.name)

@router.callback_query(F.data.startswith("authorize:"))
async def auth_start_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()

    offer_id_str = callback.data.split(':')[1]
    if offer_id_str != '0':
        offer_id = int(offer_id_str)
        await state.update_data(offer_id=offer_id)

    await auth_start(callback.message, state, callback.from_user.first_name)

@router.message(MainMenu.profile, F.text == "Заполнить профиль заново")
async def auth_start_msg(msg: Message, state: FSMContext):
    await auth_start(msg, state, msg.from_user.first_name)

@router.message(Auth.name)
async def auth_name(msg: Message, state: FSMContext):
    maxNameLen = 100
    if len(msg.text) > maxNameLen:
        await msg.answer(f"Име не может быть длиннее {maxNameLen} символов")
        return
    
    kb = ReplyKeyboardRemove()

    data = await state.get_data()
    if "user" in data:
        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text=data["user"]["city"])]
        ], resize_keyboard=True)

    await msg.answer("Из какого Вы города?", reply_markup=kb)

    await state.update_data(name=msg.text)
    await state.set_state(Auth.city)

@router.message(Auth.city)
async def auth_city(msg: Message, state: FSMContext):
    if not msg.text:
        await msg.answer("Введите название города")
        return
    await state.update_data(city=normalize_city(msg.text))

    data = await state.get_data()
    kb = ReplyKeyboardRemove()
    if "user" in data:
        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Оставить текущее описание")],
        ], resize_keyboard=True)

    txt = "<b>Расскажите о себе, и я найду лучшие объявления для Вас</b>\n\nПример: Студент 3-го курса, работаю удалённо, не курю, не устраиваю вечеринок. Ищу уютную двушку до 50к"
    await msg.answer(txt, parse_mode="HTML", reply_markup=kb)
    await state.set_state(Auth.descr)

@router.message(Auth.descr)
async def auth_descr(msg: Message, state: FSMContext):
    if not msg.text:
        await msg.answer("Нужно ввести текст")
        return
    
    data = await state.get_data()
    
    if "user" in data and msg.text == "Оставить текущее описание":
        await state.update_data(descr=data["user"]["description"])
    else:
        await state.update_data(descr=msg.text)

    kb_array = [[KeyboardButton(text="Пропустить")]]
    if "user" in data:
        kb_array.append([KeyboardButton(text="Оставить текущие фотографии")])

    kb = ReplyKeyboardMarkup(keyboard=kb_array, resize_keyboard=True)
    await msg.answer("Пожалуйста, отправьте фотографию с вашим лицом. Профилям без лица меньше доверяют", reply_markup=kb)
    await state.set_state(Auth.media_files)

@router.message(Auth.media_files, F.text == "Завершить")
async def finalize_auth_handler(msg: Message, state: FSMContext):
    data = await state.get_data()
    if "media_files" not in data:
        return
    await finalize_auth(msg, state)

async def finalize_auth(msg: Message, state: FSMContext):
    data = await state.get_data()
    print("SUCCESS\n", data)

    # TODO: отправить данные на сервер и расставить флаги с помощью LLM
    return
    user = UserVisibleData(
        name=data["name"],
        age=int(data["age"]),
        city=data["city"],
        description=data.get("descr", ""),
        media_files=data.get("media_files", [os.getenv("NO_PHOTO_FILE_ID")]),
        details=Ruleset(
            smoking=data["smoking"],
            children=data["children"],
            pets=data["pets"]
        )
    )

    await state.update_data(user=asdict(user))

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
            details=user.details
        )
        await create_user(new_user)

        # Если пользователь остановился на каком-либо объявлении
        if "offer_id" in data:
            await state.update_data(user=asdict(new_user))

    await show_profile_with_restart_keyboard(msg, state, user)

@router.message(Auth.media_files)
async def auth_media(msg: Message, state: FSMContext):
    if msg.text == "Пропустить":
        await finalize_auth(msg, state)
        return

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
    
    await send_mag(msg)

    offer_id = int(data["offer_id"])
    await show_next_offer(msg, state, offer_id)
