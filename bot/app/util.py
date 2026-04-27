from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from aiogram.fsm.context import FSMContext

async def show_main_menu(msg: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Найти жильё")],
            [KeyboardButton(text="Мои объявления")],
            [KeyboardButton(text="Мой профиль")],
        ],
        resize_keyboard=True
    )

    await msg.answer(
        "Вы в главном меню",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

async def show_profile(msg: Message, name, age, city, descr, media_files):
    caption = f"{name}, {age}, {city}"
    if descr != "":
        caption += f"\n\n{descr}"

    media_group = MediaGroupBuilder(caption=caption)

    media_files = media_files
    for file_id in media_files:
        media_group.add_photo(media=file_id)

    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Заполнить профиль заново")],
        [KeyboardButton(text="Вернуться в главное меню")],
    ], resize_keyboard=True)
    await msg.answer("Так выглядит ваш профиль:", reply_markup=keyboard)
    await msg.answer_media_group(media=media_group.build())


sent_media_group_warn: dict[tuple[int, int], bool] = {}
async def handle_media_upload(msg: Message, state: FSMContext, photo_count: int) -> bool:
    if not msg.photo:
        await msg.answer("Пожалуйста, отправьте фотографию")
        return False
    if msg.media_group_id:
        key = (msg.chat.id, msg.media_group_id)
        if key not in sent_media_group_warn:
            sent_media_group_warn[key] = True
            await msg.answer("Пожалуйста, отправляйте фотографии по одной")
        return False
    
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

    if len(media_files) <= photo_count:
        await state.update_data(media_files=media_files)

    # Достигли макс. количества фото
    if len(media_files) >= photo_count:
        return True

    msgText = "Фотография успешно загружена"
    if len(media_files) < photo_count:
        msgText += f". Вы можете отправить ещё {photo_count-len(media_files)}"

    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Завершить")]], resize_keyboard=True)

    await msg.answer(msgText, reply_markup=keyboard)
    return False


def is_int(n: str):
    try:
        int(n)
        return True
    except:
        return False
    
def is_decimal(n: str):
    from decimal import Decimal
    try:
        Decimal(n)
        return True
    except:
        return False
    
def normalize_decimal(n: str) -> str:
    return n.replace(' ', '').replace(',', '.')