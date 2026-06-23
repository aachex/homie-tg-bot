from aiogram.types import Message
from aiogram.utils.media_group import MediaGroupBuilder

from ..api.offers import HouseOffer
from ..model.enums import *
from .shared import get_relevance_emoji

async def show_offer(msg: Message, offer: HouseOffer, relevance: int = 0) -> list[Message]:
    """Отображает созданное объявление для подтверждения"""
    
    descr = f"<blockquote expandable>{offer.description}</blockquote>"

    # Данные ещё не извлечены
    if offer.flag_processing:
        # Отправляем медиагруппу с базовой информацией
        media_group = MediaGroupBuilder(caption="⌛ Обрабатывается...")
        for photo_id in offer.media_files[:10]:
            media_group.add_photo(media=photo_id)
        return await msg.answer_media_group(media=media_group.build())
    
    # ========== Форматирование цены и залога ==========
    price_parts = []

    if offer.flags.price and offer.flags.price > 0:
        price_str = f"{int(offer.flags.price):,}".replace(',', ' ')
        price_parts.append(f"💰 {price_str} ₽/месяц")

    if offer.flags.deposit and offer.flags.deposit > 0:
        deposit_str = f"{int(offer.flags.deposit):,}".replace(',', ' ')
        price_parts.append(f"🔒 Залог: {deposit_str} ₽")

    if price_parts:
        price_line = " | ".join(price_parts)
    else:
        price_line = "💰 Цена не указана"
    
    # ========== Форматирование правил ==========
    rules_lines = []
    
    # Курение
    if offer.flags.smoking is True:
        rules_lines.append("✅ Курить разрешено")
    elif offer.flags.smoking is False:
        rules_lines.append("❌ Курить запрещено")
    
    # Пол арендатора
    if offer.flags.sex == SexEnum.MALE:
        rules_lines.append("👨 Желательно мужчина")
    elif offer.flags.sex == SexEnum.FEMALE:
        rules_lines.append("👩 Желательно женщина")
    
    # Дети
    if offer.flags.children == ChildrenEnum.NONE:
        rules_lines.append("❌ Без детей")
    elif offer.flags.children == ChildrenEnum.ONE:
        rules_lines.append("✅ Можно с одним ребёнком")
    elif offer.flags.children == ChildrenEnum.TWO_PLUS or offer.flags.children == ChildrenEnum.PLANNING:
        rules_lines.append("✅ Можно с детьми")
    
    # Животные
    if offer.flags.pets == PetsEnum.NONE:
        rules_lines.append("❌ Без животных")
    elif offer.flags.pets == PetsEnum.CATS:
        rules_lines.append("✅ Можно с кошками")
    elif offer.flags.pets == PetsEnum.DOGS:
        rules_lines.append("✅ Можно с собаками")
    elif offer.flags.pets == PetsEnum.OTHER:
        rules_lines.append("✅ Можно с небольшими животными")
    elif offer.flags.pets == PetsEnum.ANY:
        rules_lines.append("🐾 Можно с любыми животными")
    
    # Количество проживающих
    if offer.flags.occupants_count is not None:
        rules_lines.append(f"👥 Максимум {offer.flags.occupants_count} чел.")
    
    # Уровень шума
    if offer.flags.noise_lvl == NoiseLvlEnum.QUIET:
        rules_lines.append("🔇 Не шуметь")
    elif offer.flags.noise_lvl == NoiseLvlEnum.LOUD:
        rules_lines.append("📢 Можно шуметь")
    
    # Работа из дома
    if offer.flags.works_from_home is True:
        rules_lines.append("💻 Желательно работа из дома")
    elif offer.flags.works_from_home is False:
        rules_lines.append("🏢 Желательно работа в офисе")
    
    # Алкоголь
    if offer.flags.alcohol == AlcoholEnum.NEVER:
        rules_lines.append("🍷 Только непьющие")
    elif offer.flags.alcohol == AlcoholEnum.RARE:
        rules_lines.append("🍷 Редко пьющие допустимы")
    elif offer.flags.alcohol == AlcoholEnum.REGULAR:
        rules_lines.append("🍷 Алкоголь разрешён")
    
    # Возраст
    if offer.flags.age_min is not None and offer.flags.age_max is not None:
        if offer.flags.age_min == offer.flags.age_max:
            rules_lines.append(f"🎂 Возраст: {offer.flags.age_min}")
        else:
            rules_lines.append(f"🎂 Возраст: {offer.flags.age_min}–{offer.flags.age_max}")
    elif offer.flags.age_min is not None:
        rules_lines.append(f"🎂 Возраст: от {offer.flags.age_min}")
    elif offer.flags.age_max is not None:
        rules_lines.append(f"🎂 Возраст: до {offer.flags.age_max}")
    
    # Формируем итоговый текст
    if rules_lines:
        rules_lines[0] = "<blockquote expandable>" + rules_lines[0]
        rules_lines[-1] += "</blockquote>"
        rules_text = "\n".join(rules_lines)
    else:
        rules_text = "<blockquote>⚪ Нет особых требований</blockquote>"
    
    # Формирование релевантности
    relevance_text = ""
    if relevance > 0:
        emoji = get_relevance_emoji(relevance)
        relevance_text = f"<b>{emoji} Совместимость:</b> {relevance}%"
    
    district = f", {offer.flags.district}" if offer.flags.district else ""
    
    # Заголовок с количеством комнат (если известно)
    if offer.flags.rooms_count == 0:
        title = f"Студия (#<code>{offer.id}</code>)"
    elif offer.flags.rooms_count:
        title = f"{offer.flags.rooms_count}-комнатная квартира (#<code>{offer.id}</code>)"
    else:
        title = f"Объявление #<code>{offer.id}</code>"
    
    message_text = f"""
<b>📋 {title}</b>

📍 {offer.city}{district}
{price_line}

<b>📝 Описание:</b>
{descr}

<b>📋 Требования к арендатору:</b>
{rules_text}

{relevance_text}
"""
    
    # ========== Отправка созданного объявления ==========
    media_group = MediaGroupBuilder()
    for photo_id in offer.media_files[:10]:
        media_group.add_photo(media=photo_id)
    messages = await msg.answer_media_group(media=media_group.build())
    caption_message = await msg.answer(message_text, parse_mode="HTML")
    
    messages.append(caption_message)
    return messages
