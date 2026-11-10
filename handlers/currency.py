"""
SUPER ASSISTANT - Valyuta Kursi Handleri
Markaziy Bank rasmiy kurslari va valyuta konvertori
"""
import re
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from utils.states import CurrencyStates
from services.currency_api import get_currency_rates, format_currency_text, convert_currency
from database.db import increment_user_requests
from keyboards.inline import get_currency_menu, get_back_button

currency_router = Router()

@currency_router.message(F.text == "💱 Valyuta kursi", StateFilter("*"))
@currency_router.callback_query(F.data == "menu_currency", StateFilter("*"))
async def handle_currency_menu(event: Message | CallbackQuery, state: FSMContext):
    """Valyuta bo'limini ochish va kurslarni ko'rsatish"""
    await state.clear()
    await increment_user_requests(event.from_user.id)

    if isinstance(event, CallbackQuery):
        await event.message.edit_text("⏳ <i>Markaziy Bank kurslari yuklanmoqda...</i>", parse_mode="HTML")
    else:
        wait_msg = await event.answer("⏳ <i>Markaziy Bank kurslari yuklanmoqda...</i>", parse_mode="HTML")

    rates = await get_currency_rates()
    text = format_currency_text(rates)

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(
            text=text,
            reply_markup=get_currency_menu(),
            parse_mode="HTML"
        )
        await event.answer()
    else:
        await wait_msg.delete()
        await event.answer(
            text=text,
            reply_markup=get_currency_menu(),
            parse_mode="HTML"
        )


@currency_router.callback_query(F.data == "curr_refresh", StateFilter("*"))
async def handle_currency_refresh(callback: CallbackQuery):
    """Valyuta kurslarini qayta yuklash"""
    rates = await get_currency_rates()
    text = format_currency_text(rates)

    try:
        await callback.message.edit_text(
            text=text,
            reply_markup=get_currency_menu(),
            parse_mode="HTML"
        )
    except Exception:
        pass
    await callback.answer("Kurslar yangilandi! 🔄")


@currency_router.callback_query(F.data == "curr_convert", StateFilter("*"))
async def handle_currency_convert_request(callback: CallbackQuery, state: FSMContext):
    """Konvertor rejimini yoqish"""
    await state.set_state(CurrencyStates.waiting_for_amount)

    text = (
        "💱 <b>Valyuta Konvertori</b>\n\n"
        "Hisoblamoqchi bo'lgan summa va valyutani yozing.\n\n"
        "<i>Namunalar:</i>\n"
        "• <code>100 usd</code> (100 dollarni so'mga aylantiradi)\n"
        "• <code>2500000 uzs</code> (2.5 mln so'mni dollarga aylantiradi)\n"
        "• <code>50 eur</code> (50 yevroni so'mga aylantiradi)\n"
        "• <code>5000 rub</code> (5000 rublni so'mga aylantiradi)"
    )

    await callback.message.edit_text(
        text=text,
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await callback.answer()


@currency_router.message(CurrencyStates.waiting_for_amount)
async def handle_currency_convert_input(message: Message, state: FSMContext):
    """Konvertatsiya so'rovini qabul qilish va hisoblash"""
    if message.text and message.text.startswith("/"):
        await state.clear()
        return

    user_input = message.text.strip()
    await increment_user_requests(message.from_user.id)

    match = re.search(r"([\d\s\,\.]+)\s*([a-zA-Z]{3})", user_input)

    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Yana hisoblash", callback_data="curr_convert")],
            [InlineKeyboardButton(text="💱 Valyuta kurslari", callback_data="menu_currency")],
            [InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="back_to_main")]
        ]
    )

    if not match:
        await message.answer(
            "⚠️ Noto'g'ri format! Iltimos, summa va valyutani to'g'ri kiriting.\n"
            "<i>Masalan:</i> <code>100 usd</code> yoki <code>1500000 uzs</code>",
            reply_markup=buttons,
            parse_mode="HTML"
        )
        return

    try:
        raw_num = match.group(1).replace(" ", "").replace(",", ".")
        amount = float(raw_num)
        currency_code = match.group(2).upper()

        rates = await get_currency_rates()

        if currency_code == "UZS":
            res_usd = convert_currency(amount, "UZS", "USD", rates)
            res_eur = convert_currency(amount, "UZS", "EUR", rates)
            res_rub = convert_currency(amount, "UZS", "RUB", rates)
            result_text = (
                f"💱 <b>Konvertatsiya Natijasi:</b>\n\n"
                f"🇺🇿 Kiritilgan summa: <b>{amount:,.0f} UZS</b>\n\n"
                f"• {res_usd}\n"
                f"• {res_eur}\n"
                f"• {res_rub}"
            )
        else:
            res = convert_currency(amount, currency_code, "UZS", rates)
            result_text = (
                f"💱 <b>Konvertatsiya Natijasi:</b>\n\n"
                f"{res}"
            )

        await message.answer(text=result_text, reply_markup=buttons, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"⚠️ Hisoblashda xatolik: {e}", reply_markup=buttons)

    await state.clear()
