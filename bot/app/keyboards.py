from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Найти жильё")],
        [KeyboardButton(text="Мои объявления")],
        [KeyboardButton(text="Мой профиль")],
    ],
    resize_keyboard=True
)

skip_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Пропустить")]
    ],
    resize_keyboard=True
)