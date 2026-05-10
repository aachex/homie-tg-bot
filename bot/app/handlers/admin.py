import io

from datetime import datetime
from dateutil.relativedelta import relativedelta

import matplotlib.pyplot as plt

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from .main_menu import ADMIN_IDS

from ..api.stats import get_dau

from ..states import MainMenu, Admin

router = Router()

@router.message(MainMenu.main_menu, F.from_user.id.in_(ADMIN_IDS), F.text == "Админ-панель")
async def admin_panel(msg: Message, state: FSMContext):
    await state.set_state(Admin.panel)

    kb = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="⚠️ Жалобы")],
        [KeyboardButton(text="Главное меню")]
    ], resize_keyboard=True)
    await msg.answer("👑 Добро пожаловать в панель администраторов", parse_mode="HTML", reply_markup=kb)

@router.message(StateFilter(Admin.panel, Admin.stats_overview), F.text == "📊 Статистика")
async def stats_overview(msg: Message, state: FSMContext):
    await state.set_state(Admin.stats_overview)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Активные пользователи", callback_data="stats_dau"), InlineKeyboardButton(text="Новые пользователи", callback_data="stats_newusers")],
        [InlineKeyboardButton(text="Лайки объявлений", callback_data="stats_offerslikes"), InlineKeyboardButton(text="Просмотры объявлений", callback_data="stats_offersviews")],
    ])
    await msg.answer("Какие метрики вас интересуют?", reply_markup=kb)

from datetime import datetime
import io
import matplotlib.pyplot as plt
from aiogram.types import BufferedInputFile
from dateutil.relativedelta import relativedelta

@router.callback_query(Admin.stats_overview, F.data == "stats_dau")
async def stats_dau(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    now = datetime.now()
    month_ago = now - relativedelta(months=1)
    month_dau = await get_dau(month_ago, now)
    
    if not month_dau:
        await callback.message.answer("📊 Недостаточно данных для построения графика")
        return
    
    # Преобразуем строковые даты в datetime
    dates = []
    dau_values = []
    for item in month_dau:
        date_str = item.date
        # Поддержка формата "2024-01-01T00:00:00Z" и "2024-01-01T00:00:00+00:00"
        if date_str.endswith('Z'):
            date_str = date_str[:-1] + '+00:00'
        date_obj = datetime.fromisoformat(date_str)
        dates.append(date_obj)
        dau_values.append(item.dau)
    
    # Строим график
    plt.figure(figsize=(12, 6))
    plt.plot(dates, dau_values, marker='o', linestyle='-', color='#2E86AB', linewidth=2, markersize=4)
    plt.fill_between(dates, dau_values, alpha=0.3, color='#2E86AB')
    
    plt.title('📈 Ежедневная активность (DAU) за последний месяц', fontsize=14, fontweight='bold')
    plt.xlabel('Дата', fontsize=12)
    plt.ylabel('Активных пользователей', fontsize=12)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.xticks(rotation=45, ha='right')
    
    # Подписи значений (опционально)
    for i, (date, dau) in enumerate(zip(dates, dau_values)):
        if dau > 0:
            plt.annotate(str(dau), (date, dau), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=8)
    
    plt.tight_layout()
    
    # Сохраняем в буфер
    image_stream = io.BytesIO()
    plt.savefig(image_stream, format='png', dpi=100)
    image_stream.seek(0)
    plt.close()
    
    # Статистика
    avg_dau = sum(dau_values) / len(dau_values)
    max_dau = max(dau_values)
    max_date = dates[dau_values.index(max_dau)]
    
    caption = (
        f"📊 **Статистика DAU за месяц**\n\n"
        f"📅 Период: {dates[0].strftime('%d.%m.%Y')} — {dates[-1].strftime('%d.%m.%Y')}\n"
        f"👥 Средняя активность: **{avg_dau:.1f}** пользователей в день\n"
        f"🔥 Пик активности: **{max_dau}** ({max_date.strftime('%d.%m.%Y')})\n"
        f"📈 Всего активных дней: {len([d for d in dau_values if d > 0])}"
    )
    
    photo_file = BufferedInputFile(image_stream.read(), filename="dau_chart.png")
    await callback.message.answer_photo(photo=photo_file, caption=caption, parse_mode="Markdown")
