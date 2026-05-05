from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from ..api.users import UserVisibleData
from ..states import Auth

async def show_profile(msg: Message, user: UserVisibleData):
    caption = f"{user.name}, {user.age}, {user.city}"
    if user.description != "":
        caption += f"\n\n{user.description}"

    media_group = MediaGroupBuilder(caption=caption)

    for file_id in user.media_files:
        media_group.add_photo(media=file_id)

    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Заполнить профиль заново")],
        [KeyboardButton(text="В главное меню")],
    ], resize_keyboard=True)
    await msg.answer("Так выглядит ваш профиль:", reply_markup=keyboard)
    await msg.answer_media_group(media=media_group.build())

async def show_unauthorized(msg: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Заполнить профиль", callback_data="authorize")]
    ], resize_keyboard=True)
    txt = "Кажется, у вас ещё нет профиля. Чтобы лайкать объявления и создавать свои, нужно заполнить профиль. Это займёт не больше минуты"
    await msg.answer(txt, reply_markup=kb)
