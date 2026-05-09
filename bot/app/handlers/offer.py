from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.fsm.context import FSMContext

from .main_menu import main_menu as show_main_menu

from ..util.offer import show_offer
from ..util.auth import show_profile
from ..util.shared import is_int, handle_media_upload, normalize_city
from ..keyboards import skip_keyboard, evaluate_keyboard, yes_no_keyboard

from ..api.users import get_user_by_id
from ..api.offers import get_user_offers, create_offer, get_offer_by_id, set_active_offer, delete_offer, get_offer_likes, delete_like, HouseOfferCreate

from ..states import OfferCreate, Offer, MainMenu
from ..model.ruleset import Ruleset

router = Router()

# ========== Просмотр своих объявлений ==========

@router.message(
    StateFilter(
        MainMenu.main_menu,
        OfferCreate.finalize,
        *Offer.__states__),
    F.text == "Мои объявления"
)
async def my_offers(msg: Message, state: FSMContext):
    await state.clear()
    await state.set_state(MainMenu.my_offers)

    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Главное меню")]], resize_keyboard=True)
    await msg.answer(
        "Ниже представлены ваши объявления.\nАктивные отмечены 🟢зелёным цветом",
        reply_markup=kb)

    offers = await get_user_offers(msg.from_user.id)

    keyboard = InlineKeyboardBuilder()
    keyboard.row(InlineKeyboardButton(text="Создать объявление", callback_data="create_offer", style="primary"))

    for offer in offers:
        btn_txt = offer.title
        if offer.likes_count > 0:
            likes_cnt = str(offer.likes_count) if offer.likes_count < 99 else "99+"
            btn_txt += f" | {likes_cnt}❤️"

        btn = InlineKeyboardButton(text=btn_txt, callback_data=f"show_offer:{offer.id}:{offer.likes_count}")
        if offer.is_active:
            btn.style = "success"
        keyboard.add(btn)

    markup = keyboard.adjust(1).as_markup()
    markup.resize_keyboard = True
    await msg.answer(
        "👇 Нажмите на объявление, чтобы посмотреть детали:",
        reply_markup=markup)

@router.callback_query(MainMenu.my_offers, F.data.startswith("show_offer:"))
async def show_house_offer(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()

    offer_id = int(callback.data.split(':')[1])
    offer = await get_offer_by_id(offer_id)

    await state.update_data(offer_id=offer_id)
    await state.update_data(offer_title=offer.title)

    kb_array = [
        [KeyboardButton(text="Отключить объявление")],
        [KeyboardButton(text="Назад")],
    ]
    
    txt = f"🟢 Объявление #{offer_id}"
    await state.set_state(Offer.active_offer_interact)
    
    if not offer.is_active:
        kb_array = [
            [KeyboardButton(text="💡Включить объявление")],
            [KeyboardButton(text="Назад")],
            [KeyboardButton(text="Удалить объявление", style="danger")]
        ]
        txt = f"<b>🔴 Объявление #{offer_id} (отключено)</b>"
        await state.set_state(Offer.inactive_offer_interact)

    likes_count = int(callback.data.split(':')[2])
    if likes_count > 0:
        kb_array.insert(1, [KeyboardButton(text=f"Посмотреть интересующихся ({likes_count})")])
    
    kb = ReplyKeyboardMarkup(keyboard=kb_array)
    kb.resize_keyboard = True
    await callback.message.answer(txt, reply_markup=kb, parse_mode="HTML")

    await show_offer(callback.message, offer)

@router.message(StateFilter(Offer.active_offer_interact, Offer.inactive_offer_interact), F.text == "Назад")
@router.message(StateFilter(Offer.offer_deact, Offer.offer_del), F.text == "Отмена")
async def back_to_my_offers(msg: Message, state: FSMContext):
    await my_offers(msg, state)

# ========== Взаимодействие с активным объявлением ==========

@router.message(Offer.active_offer_interact, F.text == "Отключить объявление")
async def deactivate_offer_warn(msg: Message, state: FSMContext):
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Да, отключить объявление")],
        [KeyboardButton(text="Отмена")],
    ], resize_keyboard=True)
    txt = "🔇 Отключение скроет объявление из поиска.\nИспользуйте эту возможность, когда арендатор уже найден или предложение временно неактуально."
    await msg.answer(txt, reply_markup=kb)
    await state.set_state(Offer.offer_deact)

@router.message(Offer.offer_deact, F.text == "Да, отключить объявление")
async def deactivate_offer(msg: Message, state: FSMContext):
    # Деактивация объявления на стороне API
    data = await state.get_data()
    offer_id = int(data["offer_id"])    
    await set_active_offer(offer_id, False)

    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Мои объявления")]], resize_keyboard=True)
    txt = f"Объявление #{offer_id} отключено. Его можно удалить или снова активировать во вкладке <b>Мои объявления</b>"
    await msg.answer(txt, reply_markup=kb, parse_mode="HTML")

# ========== Взаимодействие с неактивным объявлением ==========

@router.message(Offer.inactive_offer_interact, F.text == "💡Включить объявление")
async def activate_offer(msg: Message, state: FSMContext):
    # Активация объявления на стороне API
    data = await state.get_data()
    offer_id = int(data["offer_id"])    
    await set_active_offer(offer_id, True)

    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Мои объявления")]], resize_keyboard=True)
    txt = f"Объявление #{offer_id} снова активно!"
    await msg.answer(txt, reply_markup=kb)

@router.message(Offer.inactive_offer_interact, F.text == "Удалить объявление")
async def del_offer_warn(msg: Message, state: FSMContext):
    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Я понимаю, удалить объявление", style="danger")],
        [KeyboardButton(text="Отмена")]
    ], resize_keyboard=True)
    await msg.answer("❗Удалённые объявления не восстановить", reply_markup=kb)
    await state.set_state(Offer.offer_del)

@router.message(Offer.offer_del, F.text == "Я понимаю, удалить объявление")
async def del_offer(msg: Message, state: FSMContext):
    data = await state.get_data()
    offer_id = int(data["offer_id"])    
    await delete_offer(offer_id)

    kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Мои объявления")]], resize_keyboard=True)
    txt = f"Объявление #{offer_id} удалено"
    await msg.answer(txt, reply_markup=kb)

# ========== Создание объявления ==========

@router.callback_query(MainMenu.my_offers, F.data == "create_offer")
async def create_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()

    keyboard = ReplyKeyboardRemove()
    user = await get_user_by_id(callback.from_user.id)
    if user:
        # Добавляем подсказку
        keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=user.city)]], resize_keyboard=True)

    await callback.message.answer("В каком городе находится ваша недвижимость?", reply_markup=keyboard)

    await state.set_state(OfferCreate.city)

@router.message(OfferCreate.city)
async def select_city(msg: Message, state: FSMContext):
    if not msg.text:
        await msg.answer("Пожалуйста, введите название города")
        return
    
    await state.update_data(city=normalize_city(msg.text))
    await msg.answer("Где находится объект? Укажите район или улицу", reply_markup=skip_keyboard)
    await state.set_state(OfferCreate.district)

@router.message(OfferCreate.district)
async def enter_district(msg: Message, state: FSMContext):
    if msg.text != "Пропустить":
        await state.update_data(district=msg.text)
        
    await msg.answer("Разрешено курить?", reply_markup=yes_no_keyboard)
    await state.set_state(OfferCreate.smoking)

@router.message(OfferCreate.smoking, F.text.in_({"✅ Да", "❌ Нет"}))
async def select_smoking(msg: Message, state: FSMContext):
    allowed_smoking = (msg.text == "✅ Да")
    await state.update_data(smoking=allowed_smoking)

    await msg.answer("Можно с детьми?", reply_markup=yes_no_keyboard)
    await state.set_state(OfferCreate.children)

@router.message(OfferCreate.children, F.text.in_({"✅ Да", "❌ Нет"}))
async def select_children(msg: Message, state: FSMContext):
    allowed_children = (msg.text == "✅ Да")
    await state.update_data(children=allowed_children)

    await msg.answer("Можно с животными?", reply_markup=yes_no_keyboard)
    await state.set_state(OfferCreate.pets)

@router.message(OfferCreate.pets, F.text.in_({"✅ Да", "❌ Нет"}))
async def select_pets(msg: Message, state: FSMContext):
    allowed_pets = (msg.text == "✅ Да")
    await state.update_data(pets=allowed_pets)

    txt = "Введите краткое название вашего объявления\n\n<i>Пример:</i> Уютная комната в общежитии"
    await msg.answer(txt, parse_mode="HTML", reply_markup=ReplyKeyboardRemove())
    await state.set_state(OfferCreate.title)

@router.message(OfferCreate.title)
async def enter_title(msg: Message, state: FSMContext):
    if not msg.text:
        await msg.answer("Нужно написать название")
        return
    
    await state.update_data(title=msg.text)

    txt = "Укажите, сколько рублей в месяц стоит аренда вашей недвижимости. Этот этап можно пропустить"
    await msg.answer(txt, reply_markup=skip_keyboard)
    await state.set_state(OfferCreate.price)

@router.message(OfferCreate.price)
async def enter_price(msg: Message, state: FSMContext):
    if msg.text != "Пропустить":
        price_str = msg.text.replace(' ', '') # Удаление пробелов
        if not is_int(price_str):
            await msg.answer("Укажите целое число")
            return
        await state.update_data(price=price_str)

    txt = "Напишите подробное описание вашего объявления. Так Вы повысите вероятность найти арендатора"
    await msg.answer(txt, reply_markup=skip_keyboard)
    await state.set_state(OfferCreate.description)

@router.message(OfferCreate.description)
async def enter_descr(msg: Message, state: FSMContext):
    if not msg.text:
        await msg.answer("Нужно ввести текст")
        return
    if msg.text != "Пропустить":
        await state.update_data(descr=msg.text)
    
    await msg.answer("Теперь нужно отправить фотографии вашей недвижимости. Чем больше — тем лучше", reply_markup=ReplyKeyboardRemove())
    await state.set_state(OfferCreate.media)

@router.message(OfferCreate.media, F.text == "Завершить")
async def finalize_create_offer(msg: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    await state.set_state(OfferCreate.finalize)

    offer = HouseOfferCreate(
        owner_id=msg.from_user.id,
        title=data["title"],
        description=data.get("descr", ""),
        city=data["city"],
        district=data.get("district", ""),
        price=int(data.get("price", 0)),
        media_files=data["media_files"],
        ruleset=Ruleset(
            smoking=bool(data["smoking"]),
            children=bool(data["children"]),
            pets=bool(data["pets"])
        )
    )

    await create_offer(offer)

    await show_offer(msg, offer)

    keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Мои объявления")],
        [KeyboardButton(text="Главное меню")]
    ], resize_keyboard=True)
    msg_text = f"<b>Готово!</b> Вы успешно создали объявление о сдаче вашей недвижимости. Для более детального взаимодействия с вашими объявлениями ищите вкладку <b>Мои объявления</b> в главном меню."
    await msg.answer(msg_text, parse_mode="HTML", reply_markup=keyboard)

@router.message(OfferCreate.media)
async def upload_media(msg: Message, state: FSMContext):
    done = await handle_media_upload(msg, state, 10)
    if done:
        await finalize_create_offer(msg, state)

# ========== Просмотр лайков ==========

@router.message(StateFilter(Offer.active_offer_interact, Offer.inactive_offer_interact), F.text.startswith("Посмотреть интересующихся"))
async def show_next_like(msg: Message, state: FSMContext):
    data = await state.get_data()

    if "user_ids" not in data:
        await msg.answer("👀", reply_markup=evaluate_keyboard)

        offer_id = int(data["offer_id"])
        likes = await get_offer_likes(offer_id)
        user_ids = [like.user_id for like in likes]
        await state.update_data(user_ids=user_ids)
        data["user_ids"] = user_ids
    
    user_ids = data["user_ids"]
    if len(user_ids) == 0:
        kb = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text="Мои объявления")],
            [KeyboardButton(text="Главное меню")]
        ], resize_keyboard=True)
        await msg.answer("Просмотрены все интересующиеся", reply_markup=kb)
        return

    user_id = user_ids[0]
    user = await get_user_by_id(user_id)
    await show_profile(msg, user)

    await state.set_state(Offer.view_likes)

@router.message(Offer.view_likes)
async def evaluate_user(msg: Message, state: FSMContext):
    if msg.text == "Главное меню":
        await show_main_menu(msg, state)
        return
    
    if msg.text != "❤️" and msg.text != "👎":
        await msg.answer("Поставьте ❤️ или 👎 этому человеку")
        return
    
    data = await state.get_data()
    user_ids = data["user_ids"]

    offer_id = int(data["offer_id"])
    user_id = int(user_ids[0])
    await delete_like(offer_id, user_id)

    if msg.text == "❤️":
        title = data["offer_title"]
        owner_name = msg.from_user.first_name if msg.from_user.first_name != "" else "Владелец"
        owner_link = f'<a href="https://t.me/{msg.from_user.username}">{owner_name}</a>'
        txt = f"Владелец объявления <b>\"{title}\"</b> готов обсудить сделку! Пишите 👉 {owner_link}"
        await msg.bot.send_message(user_id, txt, parse_mode="HTML")

    await state.update_data(user_ids=user_ids[1:])
    await show_next_like(msg, state)
