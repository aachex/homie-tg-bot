import os
import asyncio
from dataclasses import asdict

from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

from aiogram.fsm.context import FSMContext

from ..keyboards import skip_keyboard, evaluate_keyboard, yes_no_keyboard

from .main_menu import main_menu as show_main_menu

from ..util.auth import show_profile, show_unauthorized
from ..util.shared import handle_media_upload, normalize_city
from ..api.users import get_user_by_id, create_user, edit_user, User, UserCreate, UserEdit, UserFlags

from ..states import Auth, MainMenu

router = Router()

@router.message(MainMenu.main_menu, F.text == "Мой профиль")
async def my_profile(msg: Message, state: FSMContext):
    user = await get_user_by_id(msg.from_user.id)
    if user is None:
        await show_unauthorized(msg)
        return

    await state.clear()
    await state.update_data(user=asdict(user))
    await state.update_data(flag_processing=user.flag_processing)

    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Заполнить профиль заново")],
        [KeyboardButton(text="Готово")],
    ], resize_keyboard=True)
    await show_profile_with_keyboard(msg, state, user, keyboard)

async def auth_start(msg: Message, state: FSMContext, first_name: str):
    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=first_name)]], resize_keyboard=True)

    data = await state.get_data()
    if "user" in data:
        kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=data["user"]["name"])]], resize_keyboard=True)

    flag_processing = data.get("flag_processing", False)
    if flag_processing:
        await msg.answer("Пожалуйста, немного подождите...")
        return
    
    await msg.answer("Пожалуйста, введите Ваше имя", reply_markup=kb)
    await state.set_state(Auth.name)

@router.callback_query(F.data == "authorize")
async def auth_start_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
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
    if len(msg.text) > 200:
        await msg.answer("Название слишком длинное")
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
    if len(msg.text) > 1500:
        await msg.answer("Длина описания не должна превышать 1500 символов")
        return
    
    data = await state.get_data()
    
    if "user" not in data or msg.text != "Оставить текущее описание":
        await state.update_data(descr=msg.text)
    else:
        await state.update_data(descr=data["user"]["description"])

    kb_array = [[KeyboardButton(text="Пропустить")]]
    if "user" in data:
        kb_array.append([KeyboardButton(text="Оставить текущие фотографии")])

    kb = ReplyKeyboardMarkup(keyboard=kb_array, resize_keyboard=True)
    await msg.answer("Пожалуйста, отправьте фотографию с вашим лицом. Профилям без лица меньше доверяют", reply_markup=kb)
    await state.set_state(Auth.media_files)

@router.message(Auth.media_files, F.text == "Пропустить")
async def skip_media(msg: Message, state: FSMContext):
    await state.update_data(media_files=[os.getenv("NO_PHOTO_FILE_ID")])
    await finalize_auth(msg, state)

@router.message(Auth.media_files, F.text == "Оставить текущие фотографии")
async def leave_previous_media(msg: Message, state: FSMContext):
    data = await state.get_data()
    if "user" not in data:
        return

    previous_media_files = data["user"]["media_files"]
    await state.update_data(media_files=previous_media_files)
    await finalize_auth(msg, state)

# Хранилище для временного сбора альбомов
temp_albums: dict[str, list[Message]] = {}

@router.message(Auth.media_files, F.media_group_id)
async def handle_album(msg: Message, state: FSMContext):
    """
    Обработчик медиагруппы (альбома) — собирает все file_id из всех фото
    """
    album_key = f"{msg.chat.id}_{msg.media_group_id}"
    
    if album_key not in temp_albums:
        temp_albums[album_key] = []
        # Запускаем таймер для финализации альбома
        asyncio.create_task(finalize_album(msg, state, album_key))
    
    temp_albums[album_key].append(msg)

async def finalize_album(msg: Message, state: FSMContext, album_key: str):
    """
    Финализирует сбор альбома и обрабатывает все file_id
    """
    await asyncio.sleep(3)  # Ждём, пока придут все сообщения альбома
    
    if album_key not in temp_albums:
        return
    
    messages = temp_albums[album_key]
    
    # Собираем все file_id из альбома
    all_file_ids = []
    
    for msg in messages:
        if msg.photo:
            # Берём самое большое фото (последний элемент)
            file_id = msg.photo[-1].file_id
            all_file_ids.append(file_id)
    
    # Сохраняем полученные фотографии
    await state.update_data(media_files=all_file_ids)
    
    # Очищаем хранилище
    del temp_albums[album_key]

    await finalize_auth(msg, state)

async def finalize_auth(msg: Message, state: FSMContext):
    data = await state.get_data()

    user = UserCreate(
        id=msg.from_user.id,
        name=data["name"],
        city=data["city"],
        description=data["descr"],
        media_files=data["media_files"],
    )

    if "user" in data:
        # Если в fsm есть старые данные пользователя, то значит он 
        # уже регистрировался и нужно редактировать его профиль, а не создавать
        user_edit = UserEdit(
            name=user.name,
            city=user.city,
            description=user.description,
            media_files=user.media_files,
        )
        await edit_user(msg.from_user.id, user_edit)
    else:
        await create_user(user)
    
    await state.update_data(user=asdict(user))
    await state.update_data(flag_processing=True)

    user = User(
        id=user.id,
        name=user.name,
        city=user.city,
        description=user.description,
        media_files=user.media_files,
        flag_processing=True
    )

    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Главное меню")],
    ], resize_keyboard=True)
    await show_profile_with_keyboard(msg, state, user, keyboard)

async def show_profile_with_keyboard(msg: Message, state: FSMContext, user: User, keyboard: ReplyKeyboardMarkup):
    await state.set_state(MainMenu.profile)
    
    await msg.answer("Так выглядит ваш профиль", reply_markup=keyboard)
    await show_profile(msg, user)
