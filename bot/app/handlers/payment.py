from math import floor

from aiogram import Bot, Router, F
from aiogram.types import Message, LabeledPrice
from aiogram.types import PreCheckoutQuery

from model.enums import PremiumTariff
from api.users import renew_premium

router = Router()

PRICE_PER_DAY = 70
PRICE_BY_TARIFF = [
    LabeledPrice(label="Неделя", amount=PRICE_PER_DAY * 7),
    LabeledPrice(label="30 дней", amount=floor(PRICE_PER_DAY * 30 * 0.8)),
    LabeledPrice(label="90 дней", amount=floor(PRICE_PER_DAY * 90 * 0.5)),
]

DURATION_DAYS = {
    PremiumTariff.WEEK: 7,
    PremiumTariff.MONTH: 30,
    PremiumTariff.THREE_MONTHS: 90,
}

@router.pre_checkout_query()
async def on_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

@router.message(F.successful_payment)
async def on_successful_payment(msg: Message):
    payment_info = msg.successful_payment
    payload = payment_info.invoice_payload.split(":")

    if payload[0] != "premium":
        return

    tariff = PremiumTariff(payload[1])

    user_id = msg.from_user.id
    days = DURATION_DAYS[tariff]

    await renew_premium(user_id=user_id, days=days)

    await msg.answer("✅ Оплата прошла успешно! Премиум-доступ активирован.")

async def send_invoice(bot: Bot, chat_id: int, tariff: PremiumTariff):
    """Отправляет счёт на выбранный тариф."""
    payload = f"premium:{tariff.value}:{chat_id}"
    DURATION_DAYS = DURATION_DAYS[tariff]

    await bot.send_invoice(
        chat_id=chat_id,
        title="🌟 Премиум-доступ",
        description=f"Доступ ко всем функциям бота на {DURATION_DAYS} дней",
        provider_token="",
        currency="XTR",
        prices=PRICE_BY_TARIFF[tariff],
        payload=payload,
        start_parameter="premium_sub",
    )
