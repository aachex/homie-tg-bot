from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

sent_media_group_warn: dict[tuple[int, int], bool] = {}
async def handle_media_upload(msg: Message, state: FSMContext, photo_count: int) -> bool:
    if not msg.photo:
        await msg.answer("Пожалуйста, отправьте фотографию")
        return False
    if msg.media_group_id:
        key = (msg.chat.id, msg.media_group_id)
        if key not in sent_media_group_warn:
            sent_media_group_warn[key] = True
            await msg.answer("Пожалуйста, отправляйте фотографии по одной")
        return False
    
    # Очистка
    keys_to_delete = [key for key in sent_media_group_warn.keys() if key[0] == msg.chat.id]
    for key in keys_to_delete:
        del sent_media_group_warn[key]
    
    file_id = msg.photo[-1].file_id
        
    data = await state.get_data()
    if "media_files" not in data:
        data["media_files"] = []

    media_files = data["media_files"]
    media_files.append(file_id)

    if len(media_files) <= photo_count:
        await state.update_data(media_files=media_files)

    # Достигли макс. количества фото
    if len(media_files) >= photo_count:
        return True

    msgText = "Фотография успешно загружена"
    if len(media_files) < photo_count:
        msgText += f". Вы можете отправить ещё {photo_count-len(media_files)}"

    keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Завершить")]], resize_keyboard=True)

    await msg.answer(msgText, reply_markup=keyboard)
    return False

def normalize_city(city: str) -> str:
    """
    Приводит название города к единому регистру с учётом особенностей.
    Примеры:
    - "РОСТОВ-НА-ДОНУ" -> "Ростов-на-Дону"
    - "САНКТ-ПЕТЕРБУРГ" -> "Санкт-Петербург"
    - "нижний новгород" -> "Нижний Новгород"
    """
    city = city.strip().lower()
    
    # Список слов, которые всегда должны быть с маленькой буквы
    lowercase_exceptions = ['и', 'на', 'в', 'под', 'над', 'за', 'при', 'без', 'до', 'из']
    
    # Список слов, которые должны быть с большой буквы
    uppercase_exceptions = {
        'санкт': 'Санкт-',
        'рост': 'Рост',
        'великий': 'Великий',
        'нижний': 'Нижний'
    }
    
    # Разбиваем на части (по пробелам и дефисам)
    parts = []
    for part in city.replace('-', ' - ').split():
        if part in lowercase_exceptions:
            parts.append(part)
        elif part in uppercase_exceptions:
            parts.append(uppercase_exceptions[part])
        else:
            parts.append(part.capitalize())
    
    result = ' '.join(parts).replace(' - ', '-')
    
    return result

def is_int(n: str):
    try:
        int(n)
        return True
    except:
        return False
