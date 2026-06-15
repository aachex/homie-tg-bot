from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

back_to_main_menu_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Главное меню")],
], resize_keyboard=True)

skip_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Пропустить")]
    ],
    resize_keyboard=True
)

evaluate_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❤️"), KeyboardButton(text="👎")],
        [KeyboardButton(text="Главное меню")]
    ], resize_keyboard=True
)

yes_no_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="✅ Да"), KeyboardButton(text="❌ Нет")]
], resize_keyboard=True)
