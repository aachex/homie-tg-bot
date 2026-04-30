from aiogram.types import Message
from aiogram.utils.media_group import MediaGroupBuilder

from ..api.offers import HouseOfferCreate

async def show_offer(msg: Message, offer: HouseOfferCreate):
    """Отображает созданное объявление для подтверждения"""
    
    # ========== Форматирование цены ==========
    if offer.price == 0:
        price_line = "💰 Цена: Не указана"
    else:
        price_str = f"{int(offer.price):,}".replace(',', ' ')
        
        # Добавляем суффикс
        suffix = "₽/месяц" if offer.type == "RENT" else "₽"
        price_line = f"💰 Цена: {price_str} {suffix}"
    
    # ========== Тип объявления ==========
    if offer.type == "RENT":
        type_text = "🏠 Сдаётся"
    elif offer.type == "SELL":
        type_text = "💰 Продаётся"
    else:
        type_text = "📋 Объявление"
    
    # ========== Текстовое сообщение ==========
    message_text = f"""
<b>📋 {type_text}</b>

<b>🏷️ Название:</b> {offer.title}
<b>📍 Город:</b> {offer.city}
{price_line}

<b>📝 Описание:</b>
{offer.description if offer.description else '<i>—</i>'}

<b>📸 Фотографий:</b> {len(offer.media_files)}
"""
    
    # ========== Отправка созданного объявления ==========

    photos_to_send = offer.media_files
        
    media_group = MediaGroupBuilder(caption=f"{message_text}")

    for photo_id in photos_to_send:
        media_group.add_photo(media=photo_id, parse_mode="HTML")
        
    await msg.answer_media_group(media=media_group.build())

