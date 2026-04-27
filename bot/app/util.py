from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

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

    await msg.answer("Так выглядит ваш профиль:", reply_markup=ReplyKeyboardRemove())
    await msg.answer_media_group(media=media_group.build())

    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Заполнить профиль заново")],
        [KeyboardButton(text="Вернуться в главное меню")],
    ], resize_keyboard=True)
    await msg.answer("Хотите заполнить профиль заново?", reply_markup=keyboard)