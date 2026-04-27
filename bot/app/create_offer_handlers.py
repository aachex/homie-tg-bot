from aiogram import F, Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

@router.message(F.text == "Мои объявления")
async def my_offers(msg: Message):
    # TODO: get user's offers

    keyboard = InlineKeyboardBuilder()

    keyboard.adjust(1).as_markup()
    await msg.answer("Выберите объявление:", reply_markup=keyboard)