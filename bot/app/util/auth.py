from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from ..api.users import UserVisibleData
from ..states import Auth

async def show_profile(msg: Message, user: UserVisibleData):
    caption = f"{user.name}, {user.age}, {user.city}"
    
    if user.description:
        caption += f"\n\n<b>📝 О себе:</b>\n{user.description}"
    
    if user.details:
        details_parts = []
        if user.details.smoking:
            details_parts.append("— Курю")
        if user.details.children:
            details_parts.append("— Есть дети")
        if user.details.pets:
            details_parts.append("— Есть питомцы")
        
        if details_parts:
            caption += f"\n\n<b>❗ Дополнительно:</b>\n" + "\n".join(details_parts)
    
    media_group = MediaGroupBuilder(caption=caption)
    
    for file in user.media_files[:10]:
        media_group.add_photo(media=file, parse_mode="HTML")
    
    await msg.answer_media_group(media=media_group.build())

async def show_unauthorized(msg: Message, offer_id: int = 0):    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Заполнить профиль", callback_data=f"authorize:{offer_id}")]
    ], resize_keyboard=True)
    txt = """💡 <b>Чтобы оценивать объявления, нужен профиль.</b>
Создать объявление можно и без него.
Создание профиля займёт меньше минуты и откроет вам полный функционал."""
    await msg.answer(txt, reply_markup=kb, parse_mode="HTML")
