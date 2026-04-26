from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import flags

from .base_handlers import show_profile

from . import api_client
from .api_client import User

class Auth(StatesGroup):
    name = State()
    age = State()
    city = State()
    descr = State()
    media_files = State()

router = Router()

@flags.rate_limit(rate=2, key="user")
@router.message(F.text == "Мой профиль")
async def my_profile(msg: Message, state: FSMContext):
    user = await api_client.get_user_by_id(msg.from_user.id)
    if user == None:
        await msg.answer("Возникла непредвиденная ошибка на сервере. Попробуйте ещё раз")
        return
    if user.id == -1:
        await msg.answer("У вас ещё нет профиля. Нужно его создать", reply_markup=ReplyKeyboardRemove())
        await state.update_data(new_user=True)
        await auth_start(msg, state)
        return

    await show_profile(
        msg,
        name=user.name,
        age=user.age,
        city=user.city,
        descr=user.description,
        media_files=user.media_files
    )

@flags.rate_limit(rate=2, key="user")
@router.message(F.text == "Заполнить профиль заново")
async def auth_start(msg: Message, state: FSMContext):
    await msg.answer("Пожалуйста, введите Ваше имя", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Auth.name)

@flags.rate_limit(rate=2, key="user")
@router.message(Auth.name)
async def auth_name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await msg.answer("Сколько Вам лет?")
    await state.set_state(Auth.age)

@flags.rate_limit(rate=2, key="user")
@router.message(Auth.age)
async def auth_age(msg: Message, state: FSMContext):
    if not is_int(msg.text):
        await msg.answer("Возраст должен быть числом")
        return
    await state.update_data(age=msg.text)
    await msg.answer("Из какого вы города?")
    await state.set_state(Auth.city)

@flags.rate_limit(rate=2, key="user")
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

@flags.rate_limit(rate=2, key="user")
@router.message(Auth.descr)
async def auth_descr(msg: Message, state: FSMContext):
    if not msg.text:
        await msg.answer("Нужно ввести текст")
        return
    if msg.text != "Пропустить":
        await state.update_data(descr=msg.text)

    await msg.answer("Пожалуйста, отправьте фотографию с вашим лицом. Профилям без лица меньше доверяют", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Auth.media_files)

@flags.rate_limit(rate=2, key="user")
@router.message(Auth.media_files, F.text == "Завершить")
async def finalize_auth(msg: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    user = User(
        id=msg.from_user.id,
        name=data["name"],
        age=int(data["age"]),
        city=data["city"],
        description=data.get("descr", ""),
        media_files=data["media_files"]
    )

    new_user = bool(data.get("new_user", False))
    if new_user:
        await api_client.create_user(user)
    else:
        await api_client.edit_user(user.id, user)

    await show_profile(msg, user.name, user.age, user.city, user.description, user.media_files)

sent_media_group_warn: dict[tuple[int, int], bool] = {}

@flags.rate_limit(rate=2, key="user")
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
    
    # Очистка
    keys_to_delete = [key for key in sent_media_group_warn.keys() if key[0] == msg.chat.id]
    for key in keys_to_delete:
        del sent_media_group_warn[key]
        
    
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

def is_int(n):
    try:
        int(n)
        return True
    except:
        return False