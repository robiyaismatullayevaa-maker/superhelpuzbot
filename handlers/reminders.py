"""
SUPER ASSISTANT - Eslatmalar va Vazifalar Handleri
SQLite ma'lumotlar bazasi orqali eslatmalarni saqlash va boshqarish
"""
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from utils.states import ReminderStates
from database.db import (
    add_reminder,
    get_user_reminders,
    delete_reminder,
    toggle_reminder_status,
    increment_user_requests
)
from keyboards.inline import get_reminders_menu, get_back_button

reminders_router = Router()

@reminders_router.message(F.text == "📝 Eslatmalar", StateFilter("*"))
@reminders_router.callback_query(F.data == "menu_reminders", StateFilter("*"))
async def handle_reminders_menu(event: Message | CallbackQuery, state: FSMContext):
    """Eslatmalar bo'limini ochish"""
    await state.clear()
    await increment_user_requests(event.from_user.id)

    text = (
        "📝 <b>Eslatmalar va Vazifalar Ro'yxati</b>\n\n"
        "Bu bo'limda siz muhim vazifalaringizni rejalashtirishingiz va saqlashingiz mumkin.\n"
        "Barcha ma'lumotlar xavfsiz SQLite bazasida saqlanadi va bot qayta yoqilganda ham yo'qolmaydi!\n\n"
        "Kerakli amalni tanlang:"
    )

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(
            text=text,
            reply_markup=get_reminders_menu(),
            parse_mode="HTML"
        )
        await event.answer()
    else:
        await event.answer(
            text=text,
            reply_markup=get_reminders_menu(),
            parse_mode="HTML"
        )


@reminders_router.callback_query(F.data == "remind_add", StateFilter("*"))
async def handle_remind_add_start(callback: CallbackQuery, state: FSMContext):
    """Yangi eslatma yaratishni boshlash (matn kiritish)"""
    await state.set_state(ReminderStates.waiting_for_text)

    text = (
        "✍️ <b>1-qadam: Eslatma matnini kiriting:</b>\n\n"
        "<i>Namunalar:</i>\n"
        "• Ingliz tili darsini takrorlash\n"
        "• Soat 15:00 da uchrashuv\n"
        "• Do'kondan kitob sotib olish"
    )

    await callback.message.edit_text(
        text=text,
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await callback.answer()


@reminders_router.message(ReminderStates.waiting_for_text)
async def handle_remind_text_input(message: Message, state: FSMContext):
    """Eslatma matni qabul qilindi, endi vaqtini so'rash"""
    if message.text and message.text.startswith("/"):
        await state.clear()
        return

    remind_text = message.text.strip()
    await state.update_data(remind_text=remind_text)
    await state.set_state(ReminderStates.waiting_for_time)

    text = (
        f"📝 Vazifa: <b>{remind_text}</b>\n\n"
        "⏰ <b>2-qadam: Eslatma vaqtini yoki muddatini kiriting:</b>\n\n"
        "<i>Namunalar:</i>\n"
        "• Bugun 18:00\n"
        "• Dushanba kuni\n"
        "• 2 kundan keyin\n"
        "• Har doim"
    )

    await message.answer(text=text, reply_markup=get_back_button(), parse_mode="HTML")


@reminders_router.message(ReminderStates.waiting_for_time)
async def handle_remind_time_input(message: Message, state: FSMContext):
    """Eslatma vaqtini qabul qilib bazaga saqlash"""
    if message.text and message.text.startswith("/"):
        await state.clear()
        return

    remind_time = message.text.strip()
    data = await state.get_data()
    remind_text = data.get("remind_text", "Nomalum vazifa")

    user_id = message.from_user.id
    await add_reminder(user_id=user_id, text=remind_text, remind_time=remind_time)
    await increment_user_requests(user_id)

    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Barcha eslatmalarim", callback_data="remind_list")],
            [InlineKeyboardButton(text="➕ Yana qo'shish", callback_data="remind_add")],
            [InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="back_to_main")]
        ]
    )

    success_text = (
        "✅ <b>Eslatma muvaffaqiyatli saqlandi!</b>\n\n"
        f"📝 Vazifa: <b>{remind_text}</b>\n"
        f"⏰ Vaqt: <b>{remind_time}</b>"
    )

    await message.answer(text=success_text, reply_markup=buttons, parse_mode="HTML")
    await state.clear()


@reminders_router.callback_query(F.data == "remind_list", StateFilter("*"))
async def handle_remind_list(callback: CallbackQuery):
    """Foydalanuvchining barcha eslatmalarini ko'rsatish"""
    user_id = callback.from_user.id
    reminders = await get_user_reminders(user_id)
    await increment_user_requests(user_id)

    if not reminders:
        buttons = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="➕ Yangi eslatma qo'shish", callback_data="remind_add")],
                [InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="back_to_main")]
            ]
        )
        await callback.message.edit_text(
            text="📭 <b>Sizda hali saqlangan eslatmalar mavjud emas.</b>\n\nPastdagi tugma orqali yangi eslatma qo'shishingiz mumkin:",
            reply_markup=buttons,
            parse_mode="HTML"
        )
        await callback.answer()
        return

    text = "📋 <b>Sizning Eslatmalaringiz va Vazifalaringiz:</b>\n\n"
    buttons_list = []

    for idx, r in enumerate(reminders, 1):
        status_icon = "✅" if r["is_done"] else "⏳"
        status_text = "Bajarildi" if r["is_done"] else "Jarayonda"
        text += f"{idx}. {status_icon} <b>{r['text']}</b>\n"
        text += f"   ⏰ Vaqt: <i>{r['remind_time']}</i> | Holat: <i>{status_text}</i>\n\n"

        toggle_icon = "🔄 Tiklash" if r["is_done"] else "✅ Bajarildi"
        buttons_list.append([
            InlineKeyboardButton(text=f"{toggle_icon} ({idx})", callback_data=f"remind_toggle_{r['id']}"),
            InlineKeyboardButton(text=f"🗑 O'chirish ({idx})", callback_data=f"remind_del_{r['id']}")
        ])

    buttons_list.append([InlineKeyboardButton(text="➕ Yangi eslatma qo'shish", callback_data="remind_add")])
    buttons_list.append([InlineKeyboardButton(text="⬅️ Eslatmalar menyusi", callback_data="menu_reminders")])

    await callback.message.edit_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons_list),
        parse_mode="HTML"
    )
    await callback.answer()


@reminders_router.callback_query(F.data.startswith("remind_toggle_"), StateFilter("*"))
async def handle_remind_toggle(callback: CallbackQuery):
    """Eslatma holatini o'zgartirish"""
    remind_id = int(callback.data.replace("remind_toggle_", ""))
    user_id = callback.from_user.id

    await toggle_reminder_status(remind_id, user_id)
    await callback.answer("Vazifa holati yangilandi! ✅")
    await handle_remind_list(callback)


@reminders_router.callback_query(F.data.startswith("remind_del_"), StateFilter("*"))
async def handle_remind_delete(callback: CallbackQuery):
    """Eslatmani o'chirish"""
    remind_id = int(callback.data.replace("remind_del_", ""))
    user_id = callback.from_user.id

    await delete_reminder(remind_id, user_id)
    await callback.answer("Eslatma o'chirildi! 🗑")
    await handle_remind_list(callback)
