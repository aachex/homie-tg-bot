from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from ..api.users import User
from ..states import Auth

async def show_profile(msg: Message, user: User):
    # Базовый заголовок
    lines = [f"👤 <b>{user.name}</b>"]
    
    # Город
    lines.append(f"📍 <b>Город:</b> {user.city}")
    
    # Количество фото
    photos_count = len(user.media_files)
    lines.append(f"📸 <b>Фото:</b> {photos_count}")
    
    # Флаги (user.flags)
    if user.flags:
        flag_lines = []
        
        # Курение
        if user.flags.smoking is True:
            flag_lines.append("🚬 Курю")
        elif user.flags.smoking is False:
            flag_lines.append("🚭 Не курю")
        
        # Дети
        if user.flags.children:
            children_map = {
                "zero": "👶 Без детей",
                "one": "👶 Один ребёнок",
                "two+": "👶👶 Двое и более детей",
                "planning": "🤰 Планируем ребёнка"
            }
            if user.flags.children.value in children_map:
                flag_lines.append(children_map[user.flags.children.value])
        
        # Животные
        if user.flags.pets:
            pets_map = {
                "cats": "🐱 Есть кошки",
                "dogs": "🐶 Есть собаки",
                "other": "🐾 Есть другие животные"
            }
            if user.flags.pets.value in pets_map:
                flag_lines.append(pets_map[user.flags.pets.value])
        
        # Количество проживающих
        if user.flags.occupants_count:
            flag_lines.append(f"👥 Проживает: {user.flags.occupants_count} чел.")
        
        # Уровень шума
        if user.flags.noise_lvl:
            noise_map = {
                "quiet": "🔇 Тихий",
                "normal": "🔊 Обычный",
                "loud": "📢 Громкий"
            }
            if user.flags.noise_lvl.value in noise_map:
                flag_lines.append(noise_map[user.flags.noise_lvl.value])
        
        # Работа из дома
        if user.flags.works_from_home is True:
            flag_lines.append("💻 Работаю из дома")
        elif user.flags.works_from_home is False:
            flag_lines.append("🏢 Работаю в офисе")
        
        # Алкоголь
        if user.flags.alcohol:
            alcohol_map = {
                "never": "🍷 Не пью",
                "rare": "🍷 Пью редко",
                "regular": "🍷 Пью регулярно"
            }
            if user.flags.alcohol.value in alcohol_map:
                flag_lines.append(alcohol_map[user.flags.alcohol.value])
        
        # Возрастной диапазон
        if user.flags.age_min or user.flags.age_max:
            age_parts = []
            if user.flags.age_min:
                age_parts.append(f"от {user.flags.age_min}")
            if user.flags.age_max:
                age_parts.append(f"до {user.flags.age_max}")
            flag_lines.append(f"🎂 Возраст: {' '.join(age_parts)}")
        
        if flag_lines:
            lines.append("\n📋 <b>Обо мне:</b>")
            lines.extend(flag_lines)
    
    # Собираем итоговый caption
    caption = "\n".join(lines)
    
    # Отправка с фото или без
    if user.media_files:
        media_group = MediaGroupBuilder(caption=caption)
        for file in user.media_files[:10]:
            media_group.add_photo(media=file, parse_mode="HTML")
        await msg.answer_media_group(media=media_group.build())
    else:
        await msg.answer(caption, parse_mode="HTML")

async def show_unauthorized(msg: Message, offer_id: int = 0):    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Заполнить профиль", callback_data=f"authorize:{offer_id}")]
    ], resize_keyboard=True)
    txt = """💡 <b>Чтобы оценивать объявления, нужен профиль.</b>
Создать объявление можно и без него.
Создание профиля займёт меньше минуты и откроет вам полный функционал."""
    await msg.answer(txt, reply_markup=kb, parse_mode="HTML")
