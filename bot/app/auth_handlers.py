from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import flags

from .util import show_profile, is_int, handle_media_upload

from .api.users import create_user, edit_user, User, UserEdit

class Auth(StatesGroup):
    name = State()
    age = State()
    city = State()
    descr = State()
    media_files = State()

router = Router()

@flags.rate_limit(rate=1, key="user")
@router.message(F.text == "Мой профиль")
async def my_profile(msg: Message, state: FSMContext):
    data = await state.get_data()
    user = data["user"]

    await show_profile(
        msg,
        name=user["name"],
        age=int(user["age"]),
        city=user["city"],
        descr=user["description"],
        media_files=user["media_files"]
    )

@flags.rate_limit(rate=1, key="user")
@router.message(F.text == "Заполнить профиль заново")
async def auth_start(msg: Message, state: FSMContext):
    await msg.answer("Пожалуйста, введите Ваше имя", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Auth.name)

@flags.rate_limit(rate=1, key="user")
@router.message(Auth.name)
async def auth_name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await msg.answer("Сколько Вам лет?")
    await state.set_state(Auth.age)

@flags.rate_limit(rate=1, key="user")
@router.message(Auth.age)
async def auth_age(msg: Message, state: FSMContext):
    if not is_int(msg.text):
        await msg.answer("Возраст должен быть числом")
        return
    await state.update_data(age=msg.text)
    await msg.answer("Из какого вы города?")
    await state.set_state(Auth.city)

@flags.rate_limit(rate=1, key="user")
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

@flags.rate_limit(rate=1, key="user")
@router.message(Auth.descr)
async def auth_descr(msg: Message, state: FSMContext):
    if not msg.text:
        await msg.answer("Нужно ввести текст")
        return
    if msg.text != "Пропустить":
        await state.update_data(descr=msg.text)

    await msg.answer("Пожалуйста, отправьте фотографию с вашим лицом. Профилям без лица меньше доверяют", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Auth.media_files)

@flags.rate_limit(rate=1, key="user")
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
        await create_user(user)
    else:
        patch = UserEdit(
            name=user.name,
            age=user.age,
            city=user.city,
            description=user.description,
            media_files=user.media_files,
        )
        await edit_user(msg.from_user.id, patch)

    await show_profile(msg, user.name, user.age, user.city, user.description, user.media_files)

@flags.rate_limit(rate=1, key="user")
@router.message(Auth.media_files)
async def auth_media(msg: Message, state: FSMContext):
    done = await handle_media_upload(msg, state, 3)
    if done:
        await finalize_auth(msg, state)

