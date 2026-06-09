from math import floor

from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..model.enums import PremiumPeriod
from ..states import MainMenu
from ..api.users import renew_premium, get_user_limits, get_premium_data

router = Router()

class Tariff:
    def __init__(
            self,
            days_count: int,
            default_price: int,
            currency: str,
            discount_percent: int = 0,
        ):
        self.days_count = days_count
        self.price = floor(default_price * (1 - discount_percent / 100))
        self.currency = currency
        self.discount_percent = discount_percent

        label_parts = []
        label_parts.append(f"Премиум на {days_count} дней")
        label_parts.append(f"⭐ {default_price}" if discount_percent == 0 else f"⭐ <s>{default_price}</s> {self.price}")
        self.label = " | ".join(label_parts)

PRICE_STARS_PER_DAY = 30

TARIFFS_STARS = {
    # Неделя
    PremiumPeriod.WEEK: Tariff(days_count=7, default_price=PRICE_STARS_PER_DAY * 7, currency="XTR"),
    
    # Месяц
    PremiumPeriod.MONTH: Tariff(days_count=30, default_price=PRICE_STARS_PER_DAY * 30, currency="XTR", discount_percent=20),

    # 3 месяца
    PremiumPeriod.THREE_MONTHS: Tariff(days_count=90, default_price=PRICE_STARS_PER_DAY * 90, currency="XTR", discount_percent=50),
}

@router.message(MainMenu.main_menu, F.text == "🌟 Премиум")
async def premium(msg: Message):
    kb = InlineKeyboardBuilder()
    for tariff_key in TARIFFS_STARS:
        tariff = TARIFFS_STARS[tariff_key]

        callback_data = f"premium:{tariff_key.value}"
        btn_text = f"Премиум на {tariff.days_count} дней"
        if tariff.discount_percent > 0:
            btn_text += f" (-{tariff.discount_percent}%)"

        kb.row(InlineKeyboardButton(text=btn_text, callback_data=callback_data))

    prices = '\n'.join([tariff.label for tariff in TARIFFS_STARS.values()])
    txt = f"🌟 Премиум: безлимитные лайки, ранний доступ, приоритет в выдаче.\n\n{prices}"

    prem_data = await get_premium_data(msg.from_user.id)
    if prem_data.is_premium:
        until = prem_data.until.strftime("%d.%m.%Y")
        txt = f"<b>Ваша премиум-подписка действует до {until}. Вы можете продлить её, используя кнопки ниже.</b>\n\n" + txt

    await msg.answer(
        txt,
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("premium:"))
async def answer_invoice(callback: CallbackQuery):
    await callback.answer()

    callback_data = callback.data.split(":")
    tariff_key = PremiumPeriod(callback_data[1])

    await send_invoice(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        tariff=TARIFFS_STARS[tariff_key],
    )
    

@router.pre_checkout_query()
async def on_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

@router.message(F.successful_payment)
async def on_successful_payment(msg: Message):
    payment_info = msg.successful_payment
    payload = payment_info.invoice_payload.split(":")

    if payload[0] != "premium" or int(payload[-1]) != msg.chat.id:
        return

    user_id = msg.from_user.id
    days = int(payload[1])

    until = await renew_premium(user_id=user_id, days=days)
    until_str = until.strftime("%d.%m.%Y")

    await msg.answer(f"✅ Спасибо! Премиум-подписка продлена до <b>{until_str}.</b>", parse_mode="HTML")

async def send_invoice(bot: Bot, chat_id: int, tariff: Tariff):
    """Отправляет счёт на выбранный тариф."""
    days_count = tariff.days_count
    price = [LabeledPrice(label=tariff.label, amount=tariff.price)]
    payload = f"premium:{tariff.days_count}:{chat_id}"

    await bot.send_invoice(
        chat_id=chat_id,
        title="🌟 Премиум-доступ",
        description=f"Доступ ко всем функциям бота на {days_count} дней",
        provider_token="",
        currency=tariff.currency,
        prices=price,
        payload=payload,
        start_parameter="premium_sub",
    )

