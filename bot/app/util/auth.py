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

    for file in user.media_files:
        media_group.add_photo(media=file)
    
    await msg.answer_media_group(media=media_group.build())

async def show_unauthorized(msg: Message, offer_id: int = 0):    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Заполнить профиль", callback_data=f"authorize:{offer_id}")]
    ], resize_keyboard=True)
    txt = """💡 <b>Чтобы оценивать объявления, нужен профиль.</b>
Создать объявление можно и без него.
Создание профиля займёт меньше минуты и откроет вам полный функционал."""
    await msg.answer(txt, reply_markup=kb, parse_mode="HTML")
