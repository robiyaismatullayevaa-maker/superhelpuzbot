"""
SUPER ASSISTANT - Admin Panel Handleri
Statistika, barcha foydalanuvchilarga xabar yuborish (Broadcast)
"""
import asyncio
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS
from utils.states import AdminStates
from database.db import get_total_users_count, get_total_requests_count, get_all_users
from keyboards.inline import get_admin_menu, get_back_button

admin_router = Router()

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@admin_router.callback_query(F.data == "menu_admin")
async def handle_admin_menu(callback: CallbackQuery, state: FSMContext):
    """Admin panelni ochish"""
    await state.clear()
    user_id = callback.from_user.id

    if not is_admin(user_id):
        await callback.answer("❌ Kechirasiz, sizda Administrator huquqi mavjud emas!", show_alert=True)
        return

    text = (
        "👨‍💻 <b>SUPER ASSISTANT - Boshqaruv Paneli (Admin)</b>\n\n"
        "Xush kelibsiz, Administrator! Bu yerdan bot foydalanuvchilari statistikasini ko'rishingiz "
        "yoki barcha foydalanuvchilarga xabar yuborishingiz mumkin.\n\n"
        "Kerakli bo'limni tanlang:"
    )

    await callback.message.edit_text(
        text=text,
        reply_markup=get_admin_menu(),
        parse_mode="HTML"
    )
    await callback.answer()


@admin_router.callback_query(F.data == "admin_stats")
async def handle_admin_stats(callback: CallbackQuery):
    """Batafsil statistikani ko'rsatish"""
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.answer("❌ Ruxsat berilmagan!", show_alert=True)
        return

    total_users = await get_total_users_count()
    total_requests = await get_total_requests_count()

    stats_text = (
        "📊 <b>Botning Umumiy Statistikasi:</b>\n\n"
        f"👥 Foydalanuvchilar soni: <b>{total_users} ta</b>\n"
        f"⚡️ Jami bajarilgan so'rovlar: <b>{total_requests} ta</b>\n"
        f"💾 Ma'lumotlar bazasi: <b>SQLite (Faol)</b>\n"
        f"🟢 Bot holati: <b>Ishchi holatda</b>\n"
    )

    await callback.message.edit_text(
        text=stats_text,
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await callback.answer()


@admin_router.callback_query(F.data == "admin_broadcast")
async def handle_admin_broadcast_start(callback: CallbackQuery, state: FSMContext):
    """Barcha foydalanuvchilarga xabar yuborishni boshlash"""
    user_id = callback.from_user.id
    if not is_admin(user_id):
        await callback.answer("❌ Ruxsat berilmagan!", show_alert=True)
        return

    await state.set_state(AdminStates.waiting_for_broadcast)

    text = (
        "📢 <b>Barcha foydalanuvchilarga xabar yuborish:</b>\n\n"
        "Yubormoqchi bo'lgan xabaringizni yozing.\n"
        "<i>Eslatma: Xabar barcha ro'yxatdan o'tgan foydalanuvchilarga yetkaziladi.</i>"
    )

    await callback.message.edit_text(
        text=text,
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await callback.answer()


@admin_router.message(AdminStates.waiting_for_broadcast)
async def handle_admin_broadcast_send(message: Message, state: FSMContext):
    """Xabarni barcha foydalanuvchilarga tarqatish"""
    user_id = message.from_user.id
    if not is_admin(user_id):
        return

    users = await get_all_users()
    total = len(users)

    progress_msg = await message.answer(f"⏳ <i>Xabar {total} ta foydalanuvchiga yuborilmoqda...</i>", parse_mode="HTML")

    success_count = 0
    blocked_count = 0

    for user in users:
        target_id = user["user_id"]
        try:
            # Xabarni nusxalash (har qanday matn, rasm yoki formatni to'liq uzatadi)
            await message.send_copy(chat_id=target_id)
            success_count += 1
            await asyncio.sleep(0.05)  # Telegram limitiga tushmaslik uchun
        except Exception:
            blocked_count += 1

    report_text = (
        "📢 <b>Xabar tarqatish yakunlandi:</b>\n\n"
        f"✅ Muvaffaqiyatli yetkazildi: <b>{success_count} ta</b>\n"
        f"❌ Yetkazilmadi (bloklaganlar): <b>{blocked_count} ta</b>\n"
        f"👥 Jami: <b>{total} ta</b>"
    )

    await progress_msg.delete()
    await message.answer(text=report_text, reply_markup=get_back_button(), parse_mode="HTML")
    await state.clear()
