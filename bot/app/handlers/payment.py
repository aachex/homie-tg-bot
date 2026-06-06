from math import floor

from aiogram import Bot, Router, F
from aiogram.types import Message, LabeledPrice
from aiogram.types import PreCheckoutQuery

from model.enums import PremiumTariff

router = Router()

@router.pre_checkout_query()
async def on_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

@router.message(F.successful_payment)
async def on_successful_payment(msg: Message):
    payment_info = msg.successful_payment
    user_id = msg.from_user.id
    payload = payment_info.invoice_payload

    # TODO: activate subscription

    await msg.answer("✅ Оплата прошла успешно! Премиум-доступ активирован.")

async def send_invoice(bot: Bot, chat_id: int, tariff: PremiumTariff):
    # Создаём объект цены (одна позиция)
    PRICE_PER_DAY = 70
    PRICES = [
        LabeledPrice(label="Неделя", amount=PRICE_PER_DAY * 7),
        LabeledPrice(label="30 дней", amount=floor(PRICE_PER_DAY * 30 * 0.8)),
        LabeledPrice(label="90 дней", amount=floor(PRICE_PER_DAY * 90 * 0.5)),
    ]

    payload: dict[PremiumTariff, str] = {
        PremiumTariff.WEEK: f"week_premium_{chat_id}",
        PremiumTariff.MONTH: f"month_premium_{chat_id}",
        PremiumTariff.THREE_MONTHS: f"3months_premium_{chat_id}"
    }

    await bot.send_invoice(
        chat_id=chat_id,
        title="🌟 Премиум-доступ",
        description="Доступ ко всем функциям бота на 30 дней",
        provider_token="",
        currency="XTR",
        prices=PRICES,
        payload=payload[tariff],
        start_parameter="premium_sub",
    )
