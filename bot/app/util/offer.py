from aiogram.types import Message
from aiogram.utils.media_group import MediaGroupBuilder

from ..api.offers import HouseOffer
from ..model.enums import *

async def show_offer(msg: Message, offer: HouseOffer):
    """Отображает созданное объявление для подтверждения"""
    
    # ========== Форматирование цены ==========
    if offer.price == 0:
        price_line = "💰 Цена: Не указана"
    else:
        price_str = f"{int(offer.price):,}".replace(',', ' ')
        price_line = f"💰 Цена: {price_str} ₽/месяц"
    
    # ========== Форматирование правил ==========
    if offer.flag_processing:
        rules_text = "⏳ Обрабатывается..."
    else:
        rules_lines = []
        
        # Курение
        if offer.preferences.smoking is True:
            rules_lines.append("✅ Курить разрешено")
        elif offer.preferences.smoking is False:
            rules_lines.append("❌ Курить запрещено")
        
        # Дети
        if offer.preferences.children == ChildrenEnum.ZERO:
            rules_lines.append("❌ Без детей")
        elif offer.preferences.children == ChildrenEnum.ONE:
            rules_lines.append("✅ Можно с одним ребёнком")
        elif offer.preferences.children == ChildrenEnum.TWO_PLUS:
            rules_lines.append("✅ Можно с детьми")
        elif offer.preferences.children == ChildrenEnum.PLANNING:
            rules_lines.append("✅ Можно планирующим ребёнка")
        
        # Животные
        if offer.preferences.pets == PetsEnum.NONE:
            rules_lines.append("❌ Без животных")
        elif offer.preferences.pets == PetsEnum.CATS:
            rules_lines.append("✅ Можно с кошками")
        elif offer.preferences.pets == PetsEnum.DOGS:
            rules_lines.append("✅ Можно с собаками")
        elif offer.preferences.pets == PetsEnum.OTHER:
            rules_lines.append("✅ Можно с другими животными")
        
        # Количество проживающих
        if offer.preferences.occupants_count is not None:
            rules_lines.append(f"👥 Максимум {offer.preferences.occupants_count} чел.")
        
        # Уровень шума
        if offer.preferences.noise_lvl == NoiseLvlEnum.QUIET:
            rules_lines.append("🔇 Только тихие")
        elif offer.preferences.noise_lvl == NoiseLvlEnum.NORMAL:
            rules_lines.append("🔊 Обычный уровень шума")
        elif offer.preferences.noise_lvl == NoiseLvlEnum.LOUD:
            rules_lines.append("📢 Можно шумные")
        
        # Работа из дома
        if offer.preferences.works_from_home is True:
            rules_lines.append("💻 Желательно работа из дома")
        elif offer.preferences.works_from_home is False:
            rules_lines.append("🏢 Желательно работа в офисе")
        
        # Алкоголь
        if offer.preferences.alcohol == AlcoholEnum.NEVER:
            rules_lines.append("🍷 Только непьющие")
        elif offer.preferences.alcohol == AlcoholEnum.RARE:
            rules_lines.append("🍷 Редко пьющие допустимы")
        elif offer.preferences.alcohol == AlcoholEnum.REGULAR:
            rules_lines.append("🍷 Алкоголь разрешён")
        
        # Возраст
        if offer.preferences.age_min is not None and offer.preferences.age_max is not None:
            rules_lines.append(f"🎂 Возраст: от {offer.preferences.age_min} до {offer.preferences.age_max}")
        elif offer.preferences.age_min is not None:
            rules_lines.append(f"🎂 Возраст: от {offer.preferences.age_min}")
        elif offer.preferences.age_max is not None:
            rules_lines.append(f"🎂 Возраст: до {offer.preferences.age_max}")
        
        rules_text = "\n".join(rules_lines) if rules_lines else "⚪ Нет особых требований"
    
    # ========== Текстовое сообщение ==========
    district = f", {offer.district}" if offer.district else ""
    message_text = f"""
<b>📋 {offer.title}</b>

<b>📍 Город:</b> {offer.city}{district}
{price_line}

<b>📝 Описание:</b>
{offer.description if offer.description else '<i>—</i>'}

<b>📸 Фотографий:</b> {len(offer.media_files)}

<b>📋 Требования к арендатору:</b>
{rules_text}
"""
    
    # ========== Отправка созданного объявления ==========
    if offer.media_files:
        media_group = MediaGroupBuilder(caption=message_text)
        for photo_id in offer.media_files[:10]:
            media_group.add_photo(media=photo_id, parse_mode="HTML")
        await msg.answer_media_group(media=media_group.build())
    else:
        await msg.answer(message_text, parse_mode="HTML")
