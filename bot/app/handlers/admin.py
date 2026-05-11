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
    
    report_ids = data["report_ids"] if "report_ids" in data else await get_pending_reports()
    
    if not report_ids:
        await msg.answer("📭 Нет необработанных жалоб")
        return
    
    # Сохраняем список ID в состояние
    await state.update_data(report_ids=report_ids)
    
    # Создаём клавиатуру со списком жалоб
    builder = InlineKeyboardBuilder()
    
    for report_id in report_ids:
        builder.add(InlineKeyboardButton(
            text=f"📋 Жалоба #{report_id}",
            callback_data=f"report_view:{report_id}"
        ))
    
    builder.adjust(1)  # По одной кнопке в ряд
    
    await msg.answer(
        f"📋 **Необработанные жалобы** (всего: {len(report_ids)})",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@router.callback_query(Admin.report_details, F.data == "reports_back")
async def reports_view_callback(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Admin.reports)

    # Получаем ID необработанных жалоб
    data = await state.get_data()
    
    report_ids = data["report_ids"] if "report_ids" in data else await get_pending_reports()
    
    if not report_ids:
        await callback.message.edit_text("📭 Нет необработанных жалоб")
        return
    
    # Сохраняем список ID в состояние
    await state.update_data(report_ids=report_ids)
    
    # Создаём клавиатуру со списком жалоб
    builder = InlineKeyboardBuilder()
    
    for report_id in report_ids:
        builder.add(InlineKeyboardButton(
            text=f"📋 Жалоба #{report_id}",
            callback_data=f"report_view:{report_id}"
        ))
    
    builder.adjust(1)  # По одной кнопке в ряд
    
    await callback.message.edit_text(
        f"📋 **Необработанные жалобы** (всего: {len(report_ids)})",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

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
