from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from aiogram.filters import StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder

from aiogram.fsm.context import FSMContext

from .main_menu import ADMIN_IDS

from ..states import MainMenu, Admin

from ..api.reports import get_pending_reports, report_by_id

router = Router()

@router.message(MainMenu.main_menu, F.from_user.id.in_(ADMIN_IDS), F.text == "Админ-панель")
async def admin_panel(msg: Message, state: FSMContext):
    await state.set_state(Admin.panel)

    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="⚠️ Жалобы")],
        [KeyboardButton(text="Главное меню")]
    ], resize_keyboard=True)
    await msg.answer("👑 Добро пожаловать в панель администраторов", parse_mode="HTML", reply_markup=kb)

@router.message(StateFilter(*Admin.__states__), F.text.startswith("⚠️ Жалобы"))
async def reports_view(msg: Message, state: FSMContext):
    await state.set_state(Admin.reports)

    # Получаем ID необработанных жалоб
    data = await state.get_data()
    
    offset = data.get("offset", 0)
    report_ids = data["report_ids"] if "report_ids" in data else await get_pending_reports(offset=offset)
    
    if not report_ids:
        await msg.answer("📭 Нет необработанных жалоб")
        return
    
    # Сохраняем список ID в состояние
    await state.update_data(report_ids=report_ids)
    
    # Создаём клавиатуру со списком жалоб
    kb = create_reports_keyboard(report_ids)
    
    await msg.answer(
        f"📋 <b>Необработанные жалобы</b> (всего: {len(report_ids)})",
        reply_markup=kb,
        parse_mode="HTML"
    )

@router.callback_query(Admin.report_details, F.data == "reports_back")
async def reports_view_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.reports)

    # Получаем ID необработанных жалоб
    data = await state.get_data()
    
    offset = data.get("offset", 0)
    report_ids = data["report_ids"] if "report_ids" in data else await get_pending_reports(offset=offset)
    
    if not report_ids:
        await callback.message.edit_text("📭 Нет необработанных жалоб")
        return
    
    # Сохраняем список ID в состояние
    await state.update_data(report_ids=report_ids)
    
    # Создаём клавиатуру со списком жалоб
    kb = create_reports_keyboard(report_ids)
    
    await callback.message.edit_text(
        f"📋 <b>Необработанные жалобы</b> (всего: {len(report_ids)})",
        reply_markup=kb,
        parse_mode="HTML"
    )

def create_reports_keyboard(report_ids: list[int]):
    builder = InlineKeyboardBuilder()
    
    for report_id in report_ids:
        builder.add(InlineKeyboardButton(
            text=f"📋 Жалоба #{report_id}",
            callback_data=f"report_view:{report_id}"
        ))
    
    builder.adjust(1)  # По одной кнопке в ряд
    
    builder.row(
        InlineKeyboardButton(text="⬅️", callback_data="reports_prev_page"),
        InlineKeyboardButton(text="➡️", callback_data="reports_next_page"),
        width=2
    )
    
    return builder.as_markup()

@router.callback_query(Admin.reports, F.data == "reports_next_page")
async def reports_next_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_offset = data.get("offset", 0)
    await state.update_data(offset=current_offset+10)
    await reports_view_callback(callback, state)

@router.callback_query(Admin.reports, F.data == "reports_prev_page")
async def reports_prev_page(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_offset = data.get("offset", 0)
    await state.update_data(offset=max(0, current_offset-10))
    await reports_view_callback(callback, state)


@router.callback_query(Admin.reports, F.data.startswith("report_view:"))
async def report_details(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.report_details)

    report_id = int(callback.data.split(':')[1])
    report = await report_by_id(report_id)
    
    if report is None:
        await callback.answer("❌ Жалоба не найдена", show_alert=True)
        return
    
    await callback.answer()
    
    # Форматируем дату
    created_at_str = report.created_at.strftime('%d.%m.%Y в %H:%M') if report.created_at else "Не указана"
    
    # Формируем текст
    text = (
        f"📋 <b>ЖАЛОБА #{report.id}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📦 <b>Объявление:</b> <code>#{report.offer_id}</code>\n"
        f"👤 <b>Пожаловался:</b> <code>{report.reporter_id}</code>\n"
        f"📅 <b>Дата:</b> {created_at_str}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 <b>Причина жалобы:</b>\n"
        f"<i>{report.reason}</i>\n"
    )
    
    # Клавиатура действий
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять жалобу", callback_data=f"report_approve:{report.id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"report_reject:{report.id}"),
        ],
        [
            InlineKeyboardButton(text="🔙 Назад к списку", callback_data="reports_back"),
        ],
    ])
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@router.message(StateFilter(*Admin.__states__), F.text == "📊 Статистика")
async def stats_overview(msg: Message, state: FSMContext):
    await state.set_state(Admin.stats_overview)
    await msg.answer("В разработке...")
