import asyncio

from datetime import datetime

from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import CommandStart

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

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

    await msg.answer("Пожалуйста, загрузите фотографию или видео с вашим лицом. Профилям без лица меньше доверяют", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Auth.media_files)

@router.message(Auth.media_files)
async def auth_media(msg: Message, state: FSMContext):
    if not msg.photo and not msg.video:
        await msg.answer("Пожалуйста, загрузите одно фото или видео")