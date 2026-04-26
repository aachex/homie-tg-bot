from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from .base_handlers import show_profile

class Auth(StatesGroup):
    name = State()
    age = State()
    city = State()
    descr = State()
    media_files = State()

router = Router()

@router.message(F.text == "Мой профиль")
async def my_profile(msg: Message):
    # TODO: get user data by id...

    await show_profile(
        msg,
        name="Артём",
        age="18",
        city="Петрозаводск",
        descr="Ищу бюджетную комнату в центре",
        media_files=["AgACAgIAAxkBAAIB3Gnt5TCKG34tV7DYkdBz-Zc7x2tRAAIZFmsbx0pxS1mW49mmcnPUAQADAgADeQADOwQ"]
    )

@router.message(F.text == "Заполнить профиль заново")
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
    if not msg.text:
        await msg.answer("Нужно ввести текст")
        return
    if msg.text != "Пропустить":
        await state.update_data(descr=msg.text)

    await msg.answer("Пожалуйста, отправьте фотографию с вашим лицом. Профилям без лица меньше доверяют", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Auth.media_files)

@router.message(Auth.media_files, F.text == "Завершить")
async def finalize_auth(msg: Message, state: FSMContext):
    data = await state.get_data()
    await show_profile(msg, data["name"], data["age"], data["city"], data.get("descr", ""), data["media_files"])
    await state.clear()

sent_media_group_warn: dict[tuple[int, int], bool] = {}

@router.message(Auth.media_files)
async def auth_media(msg: Message, state: FSMContext):
    if not msg.photo:
        await msg.answer("Пожалуйста, отправьте фотографию")
        return
    if msg.media_group_id:
        key = (msg.chat.id, msg.media_group_id)
        if key not in sent_media_group_warn:
            sent_media_group_warn[key] = True
            await msg.answer("Пожалуйста, отправляйте фотографии по одной")
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
        await finalize_auth(msg, state)
        return

    msgText = "Фотография успешно загружена"
    if len(media_files) < 3:
        msgText += f". Вы можете отправить ещё {3-len(media_files)}"

    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Завершить")]], resize_keyboard=True)

    await msg.answer(msgText, reply_markup=keyboard)
