from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .api.offers import get_user_offers, HouseOfferPreview

router = Router()

@router.message(F.text == "Мои объявления")
async def my_offers(msg: Message):
    offers = await get_user_offers(msg.from_user.id)

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Создать объявление", callback_data="create_offer", style="primary"))

    for offer in offers:
        btn = InlineKeyboardButton(text=offer.title, callback_data=f"show_offer:{id}")
        if offer.is_active:
            btn.style = "success"
        keyboard.add(btn)

    await msg.answer(
        "Ниже представлены ваши объявления. Активные отмечены 🟢зелёным цветом и находятся в начале списка",
        reply_markup=keyboard.adjust(1).as_markup())

@router.callback_query(F.data.startswith("show_offer"))
async def show_offer(data: CallbackQuery):
    offer_id = int(data.data.split(":")[1])