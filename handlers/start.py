"""
SUPER ASSISTANT - Start va Asosiy Menyu Handlerlari
Muallif: Murodilova Robiya (@byrobiye)
"""
import html
from aiogram import Router, F
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS, OWNER_NAME, OWNER_USERNAME, BOT_NAME
from database.db import add_or_update_user, get_user, increment_user_requests
from keyboards.inline import get_main_menu, get_back_button

start_router = Router()

# Doimiy pastki tezkor menyu tugmalari
reply_quick_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🏠 Asosiy menyu"), KeyboardButton(text="👤 Profil")],
        [KeyboardButton(text="🤖 AI Yordamchi"), KeyboardButton(text="🌤 Ob-havo")],
        [KeyboardButton(text="🌍 Tarjimon"), KeyboardButton(text="🧮 Kalkulyator")],
        [KeyboardButton(text="📚 Ta'lim"), KeyboardButton(text="📝 Eslatmalar")],
        [KeyboardButton(text="💱 Valyuta kursi"), KeyboardButton(text="📞 Bog'lanish")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Kerakli bo'limni tanlang..."
)

@start_router.message(CommandStart(), StateFilter("*"))
@start_router.message(Command("start"), StateFilter("*"))
@start_router.message(F.text.casefold() == "/start", StateFilter("*"))
@start_router.message(F.text == "🏠 Asosiy menyu", StateFilter("*"))
async def handle_start(message: Message, state: FSMContext):
    """Start buyrug'i: FSM holatini tozalab, foydalanuvchini ro'yxatga olish va asosiy menyuni chiqarish"""
    await state.clear()

    user_id = message.from_user.id
    raw_name = message.from_user.full_name or "Foydalanuvchi"
    safe_name = html.escape(raw_name)
    username = message.from_user.username

    # SQLite bazasiga saqlash
    try:
        await add_or_update_user(user_id, raw_name, username)
        await increment_user_requests(user_id)
    except Exception as e:
        print(f"Baza xatoligi: {e}")

    is_admin = user_id in ADMIN_IDS

    welcome_text = (
        f"Assalomu alaykum, <b>{safe_name}</b>! 👋\n\n"
        f"🌟 <b>{BOT_NAME}</b>ga xush kelibsiz!\n"
        f"Men sizning ko'p funksiyali professional shaxsiy yordamchingizman.\n\n"
        f"📌 <b>Barcha 9 ta xizmat:</b>\n"
        f"1. 🤖 <b>AI Yordamchi</b> — savol-javob, matn va g'oyalar\n"
        f"2. 🌤 <b>Ob-havo</b> — shahar bo'yicha aniq ma'lumotlar\n"
        f"3. 🌍 <b>Tarjimon</b> — o'zbek, rus, ingliz tillari\n"
        f"4. 🧮 <b>Kalkulyator</b> — arifmetik hisoblash & foizlar\n"
        f"5. 📚 <b>Ta'lim</b> — ingliz tili, testlar, qiziqarli faktlar\n"
        f"6. 📝 <b>Eslatmalar</b> — vazifalar ro'yxati (SQLite da)\n"
        f"7. 💱 <b>Valyuta kursi</b> — Markaziy Bank kurslari & konvertor\n"
        f"8. 👤 <b>Foydalanuvchi profili</b> — shaxsiy statistikangiz\n"
        f"9. 👨‍💻 <b>Admin panel</b> — boshqaruv va xabar tarqatish\n\n"
        f"👩‍💻 <b>Loyiha muallifi:</b> {OWNER_NAME} (<a href='https://t.me/{OWNER_USERNAME}'>@{OWNER_USERNAME}</a>)\n\n"
        f"Kerakli bo'limni tanlash uchun pastdagi tugmalardan birini bosing: 👇"
    )

    await message.answer(
        text=welcome_text,
        reply_markup=get_main_menu(is_admin),
        parse_mode="HTML"
    )


@start_router.callback_query(F.data == "back_to_main", StateFilter("*"))
async def handle_back_to_main(callback: CallbackQuery, state: FSMContext):
    """Har qanday bo'limdan asosiy menyuga qaytish"""
    await state.clear()
    user_id = callback.from_user.id
    is_admin = user_id in ADMIN_IDS

    text = (
        f"🏠 <b>Asosiy menyu</b>\n\n"
        f"O'zingizga kerakli bo'limni tanlang:"
    )

    try:
        await callback.message.edit_text(
            text=text,
            reply_markup=get_main_menu(is_admin),
            parse_mode="HTML"
        )
    except Exception:
        await callback.message.answer(
            text=text,
            reply_markup=get_main_menu(is_admin),
            parse_mode="HTML"
        )
    await callback.answer()


@start_router.message(F.text == "👤 Profil", StateFilter("*"))
@start_router.callback_query(F.data == "menu_profile", StateFilter("*"))
async def handle_profile(event: Message | CallbackQuery, state: FSMContext):
    """Foydalanuvchi profili va statistikasi"""
    await state.clear()
    user = event.from_user
    user_id = user.id
    is_admin = user_id in ADMIN_IDS

    db_user = await get_user(user_id)

    safe_name = html.escape(user.full_name or "Foydalanuvchi")
    username = f"@{user.username}" if user.username else "Mavjud emas"
    joined_at = db_user["joined_at"] if db_user else "Hozirgina"
    requests_count = db_user["requests_count"] if db_user else 1
    role = "👑 Administrator" if is_admin else "👤 Oddiy foydalanuvchi"

    profile_text = (
        f"👤 <b>Foydalanuvchi Profili</b>\n\n"
        f"🆔 Telegram ID: <code>{user_id}</code>\n"
        f"👤 Ism: <b>{safe_name}</b>\n"
        f"🌐 Username: {username}\n"
        f"🔰 Maqom: <b>{role}</b>\n"
        f"📅 Qo'shilgan sana: <b>{joined_at}</b>\n"
        f"⚡️ Bajarilgan so'rovlar: <b>{requests_count} ta</b>\n\n"
        f"👩‍💻 <b>Bot egasi:</b> {OWNER_NAME} (<a href='https://t.me/{OWNER_USERNAME}'>@{OWNER_USERNAME}</a>)"
    )

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(
            text=profile_text,
            reply_markup=get_back_button(),
            parse_mode="HTML"
        )
        await event.answer()
    else:
        await event.answer(
            text=profile_text,
            reply_markup=get_back_button(),
            parse_mode="HTML"
        )


@start_router.message(F.text == "📞 Bog'lanish", StateFilter("*"))
async def handle_contact_reply(message: Message, state: FSMContext):
    """Bog'lanish tugmasi"""
    await state.clear()
    text = (
        f"📞 <b>Loyiha Muallifi bilan bog'lanish:</b>\n\n"
        f"👩‍💻 <b>Ism va familiya:</b> {OWNER_NAME}\n"
        f"💬 <b>Telegram:</b> <a href='https://t.me/{OWNER_USERNAME}'>@{OWNER_USERNAME}</a>\n\n"
        f"Savollar, takliflar yoki hamkorlik bo'yicha bemalol yozishingiz mumkin!"
    )
    await message.answer(text=text, reply_markup=get_back_button(), parse_mode="HTML")
