from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏡 Найти квартиру/дом")],
        [KeyboardButton(text="Мой профиль")],
        [KeyboardButton(text="Мои объявления")],
    ],
    resize_keyboard=True
)

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
    [KeyboardButton(text="Да"), KeyboardButton(text="Нет")]
], resize_keyboard=True)
