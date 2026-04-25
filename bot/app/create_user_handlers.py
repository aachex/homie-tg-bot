from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import CommandStart
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from .base_handlers import Base, show_main_menu

class Auth(StatesGroup):
    name = State()
    age = State()
    city = State()
    descr = State()
    media_files = State()

router = Router()

@router.message(CommandStart())
async def start(msg: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Найти жильё")],
            [KeyboardButton(text="Мои объявления")],
            [KeyboardButton(text="Создать/редактировать профиль")],
        ],
        resize_keyboard=True
    )

    await msg.answer(
        "Добро пожаловать в <b>Homie!</b> Здесь вы сможете найти или продать жильё в своём городе",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.message(F.text == "Создать/редактировать профиль")
async def auth_start(msg: Message, state: FSMContext):
    await msg.answer("Пожалуйста, введите Ваше имя", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Auth.name)

@router.message(Auth.name)
async def auth_name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await msg.answer("Сколько Вам лет?")
    await state.set_state(Auth.age)

@router.message(Auth.age)
async def auth_age(msg: Message, state: FSMContext):
    await state.update_data(age=msg.text)
    await msg.answer("Из какого вы города?")
    await state.set_state(Auth.city)

@router.message(Auth.city)
async def auth_city(msg: Message, state: FSMContext):
    await state.update_data(city=msg.text)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Пропустить")]
        ],
        resize_keyboard=True
    )
    await msg.answer("Расскажите немного о себе. Данный пункт необязателен, но желателен", reply_markup=keyboard)
    await state.set_state(Auth.descr)

@router.message(Auth.descr)
async def auth_descr(msg: Message, state: FSMContext):
    if msg.text != "Пропустить":
        await state.update_data(descr=msg.text)

    await msg.answer("Пожалуйста, отправьте фотографию с вашим лицом. Профилям без лица меньше доверяют", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Auth.media_files)

@router.message(Auth.media_files, F.text == "Завершить")
async def send_profile(msg: Message, state: FSMContext):
    data = await state.get_data()

    caption = f"{data["name"]}, {data["age"]}, {data["city"]}"
    if "descr" in data:
        caption += f"\n\n{data["descr"]}"
        
    media_group = MediaGroupBuilder(caption=caption)

    media_files = data["media_files"]
    for file_id in media_files:
        media_group.add_photo(media=file_id)

    await msg.answer("Так выглядит ваш профиль:", reply_markup=ReplyKeyboardRemove())
    await msg.answer_media_group(media=media_group.build())

    await state.clear()
    await show_main_menu(msg)

@router.message(Auth.media_files)
async def auth_media(msg: Message, state: FSMContext):
    if not msg.photo:
        await msg.answer("Пожалуйста, отправьте фотографию")
        return
    
    file_id = msg.photo[-1].file_id
        
    data = await state.get_data()
    if "media_files" not in data:
        data["media_files"] = []

    media_files = data["media_files"]
    media_files.append(file_id)

    if len(media_files) <= 3:
        await state.update_data(media_files=media_files)

    # Достигли макс. количества фото
    if len(media_files) >= 3:
        await send_profile(msg, state)
        return

    msgText = "Фотография успешно загружена"
    if len(media_files) < 3:
        msgText += f". Вы можете отправить ещё {3-len(media_files)}"

    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Завершить")]], resize_keyboard=True)

    await msg.answer(msgText, reply_markup=keyboard)

