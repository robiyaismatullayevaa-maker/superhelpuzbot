"""
SUPER ASSISTANT - Kalkulyator Handleri
Oddiy hisob-kitoblar va foiz hisoblash
"""
import re
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from utils.states import CalculatorStates
from database.db import increment_user_requests
from keyboards.inline import get_calculator_menu, get_back_button

calculator_router = Router()

def safe_eval_expression(expr: str):
    """Xavfsiz matematik hisoblash"""
    clean_expr = expr.replace("x", "*").replace("X", "*").replace(":", "/").replace(",", ".")
    if not re.match(r"^[\d\s\+\-\*\/\(\)\.\%]+$", clean_expr):
        return None, "Ifodada faqat raqamlar va +, -, *, /, (, ) arifmetik belgilari bo'lishi kerak."

    try:
        result = eval(clean_expr, {"__builtins__": None}, {})
        return result, None
    except ZeroDivisionError:
        return None, "0 ga bo'lish mumkin emas!"
    except Exception:
        return None, "Matematik ifodada xatolik bor. Qaytadan tekshirib yozing."


@calculator_router.message(F.text == "🧮 Kalkulyator", StateFilter("*"))
@calculator_router.callback_query(F.data == "menu_calculator", StateFilter("*"))
async def handle_calculator_menu(event: Message | CallbackQuery, state: FSMContext):
    """Kalkulyator bo'limini ochish"""
    await state.clear()
    await increment_user_requests(event.from_user.id)

    text = (
        "🧮 <b>Kalkulyator Bo'limi</b>\n\n"
        "Quyidagi yo'nalishlardan birini tanlang:\n\n"
        "• <b>Matematik ifoda:</b> masalan, <code>25 * 4 + 150 / 2</code>\n"
        "• <b>Foiz hisoblash:</b> ma'lum bir summaning foizini aniqlash"
    )

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(
            text=text,
            reply_markup=get_calculator_menu(),
            parse_mode="HTML"
        )
        await event.answer()
    else:
        await event.answer(
            text=text,
            reply_markup=get_calculator_menu(),
            parse_mode="HTML"
        )


@calculator_router.callback_query(F.data == "calc_expr", StateFilter("*"))
async def handle_calc_expr_request(callback: CallbackQuery, state: FSMContext):
    """Matematik ifoda kiritish rejimiga o'tish"""
    await state.set_state(CalculatorStates.waiting_for_expression)

    text = (
        "🧮 <b>Matematik ifodani yozing:</b>\n\n"
        "<i>Namunalar:</i>\n"
        "• <code>(450 + 550) * 2</code>\n"
        "• <code>125000 / 5</code>\n"
        "• <code>15 * 8 - 30</code>"
    )

    await callback.message.edit_text(
        text=text,
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await callback.answer()


@calculator_router.message(CalculatorStates.waiting_for_expression)
async def handle_calc_expr_input(message: Message, state: FSMContext):
    """Matematik ifodani hisoblash va natijani ko'rsatish"""
    if message.text and message.text.startswith("/"):
        await state.clear()
        return

    user_expr = message.text.strip()
    await increment_user_requests(message.from_user.id)

    result, err = safe_eval_expression(user_expr)

    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Yana hisoblash", callback_data="calc_expr")],
            [InlineKeyboardButton(text="📊 Foiz hisoblash", callback_data="calc_percent")],
            [InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="back_to_main")]
        ]
    )

    if err:
        await message.answer(f"⚠️ <b>Xatolik:</b> {err}", reply_markup=buttons, parse_mode="HTML")
    else:
        formatted_res = f"{result:,.4f}".rstrip("0").rstrip(".") if isinstance(result, float) else f"{result:,}"
        res_text = (
            f"🧮 <b>Hisoblash Natijasi:</b>\n\n"
            f"📝 <b>Ifoda:</b> <code>{user_expr}</code>\n"
            f"✅ <b>Natija:</b> <b>{formatted_res}</b>"
        )
        await message.answer(text=res_text, reply_markup=buttons, parse_mode="HTML")

    await state.clear()


@calculator_router.callback_query(F.data == "calc_percent", StateFilter("*"))
async def handle_calc_percent_request(callback: CallbackQuery, state: FSMContext):
    """Foiz hisoblash rejimiga o'tish"""
    await state.set_state(CalculatorStates.waiting_for_percent)

    text = (
        "📊 <b>Foiz Hisoblash:</b>\n\n"
        "Summa va foiz miqdorini probel bilan ajratib yozing.\n\n"
        "<i>Namuna:</i>\n"
        "<code>500000 12</code> (500,000 ning 12 foizini hisoblaydi)"
    )

    await callback.message.edit_text(
        text=text,
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await callback.answer()


@calculator_router.message(CalculatorStates.waiting_for_percent)
async def handle_calc_percent_input(message: Message, state: FSMContext):
    """Foizni hisoblash"""
    if message.text and message.text.startswith("/"):
        await state.clear()
        return

    parts = message.text.strip().split()
    await increment_user_requests(message.from_user.id)

    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Yana foiz hisoblash", callback_data="calc_percent")],
            [InlineKeyboardButton(text="🧮 Matematik ifoda", callback_data="calc_expr")],
            [InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="back_to_main")]
        ]
    )

    if len(parts) < 2:
        await message.answer(
            "⚠️ Iltimos, summa va foizni probel bilan kiriting.\nMasalan: <code>100000 15</code>",
            reply_markup=buttons,
            parse_mode="HTML"
        )
        return

    try:
        amount = float(parts[0].replace(",", "."))
        percent = float(parts[1].replace(",", ".").replace("%", ""))

        part_val = (amount * percent) / 100
        plus_val = amount + part_val
        minus_val = amount - part_val

        res_text = (
            f"📊 <b>Foiz Hisoblash Natijasi:</b>\n\n"
            f"💰 Asosiy summa: <b>{amount:,.2f}</b>\n"
            f"📈 Foiz stavkasi: <b>{percent}%</b>\n\n"
            f"• <b>{amount:,.2f}</b> ning <b>{percent}%</b>i: <b>{part_val:,.2f}</b>\n"
            f"• Foiz qo'shilganda (+): <b>{plus_val:,.2f}</b>\n"
            f"• Foiz ayirilganda (-): <b>{minus_val:,.2f}</b>"
        )
        await message.answer(text=res_text, reply_markup=buttons, parse_mode="HTML")
    except ValueError:
        await message.answer(
            "⚠️ Raqamlarni to'g'ri kiritganingizga ishonch hosil qiling. Namuna: <code>250000 20</code>",
            reply_markup=buttons,
            parse_mode="HTML"
        )

    await state.clear()
