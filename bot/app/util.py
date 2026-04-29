from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from aiogram.fsm.context import FSMContext

from .api.users import UserVisibleData
from .api.offers import HouseOfferCreate

async def show_main_menu(msg: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Найти жильё")],
            [KeyboardButton(text="Мои объявления")],
            [KeyboardButton(text="Мой профиль")],
        ],
        resize_keyboard=True
    )

    await msg.answer(
        "Вы в главном меню",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

async def show_profile(msg: Message, user: UserVisibleData):
    caption = f"{user.name}, {user.age}, {user.city}"
    if user.description != "":
        caption += f"\n\n{user.description}"

    media_group = MediaGroupBuilder(caption=caption)

    for file_id in user.media_files:
        media_group.add_photo(media=file_id)

    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Заполнить профиль заново")],
        [KeyboardButton(text="В главное меню")],
    ], resize_keyboard=True)
    await msg.answer("Так выглядит ваш профиль:", reply_markup=keyboard)
    await msg.answer_media_group(media=media_group.build())

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


def is_int(n: str):
    try:
        int(n)
        return True
    except:
        return False
