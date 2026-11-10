"""
SUPER ASSISTANT - AI Yordamchi Handleri
Savol-javob, matn yozish va g'oyalar berish
"""
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from utils.states import AIStates
from services.ai_service import ask_ai
from database.db import increment_user_requests
from keyboards.inline import get_back_button

ai_router = Router()

@ai_router.message(F.text == "🤖 AI Yordamchi", StateFilter("*"))
@ai_router.callback_query(F.data == "menu_ai", StateFilter("*"))
async def handle_ai_menu(event: Message | CallbackQuery, state: FSMContext):
    """AI bo'limini ochish"""
    await state.clear()
    await state.set_state(AIStates.waiting_for_prompt)
    await increment_user_requests(event.from_user.id)

    text = (
        "🤖 <b>AI Yordamchi Bo'limi</b>\n\n"
        "Men sizga quyidagi vazifalarda yordam bera olaman:\n"
        "• Har qanday savollarga javob berish\n"
        "• Ijtimoiy tarmoqlar uchun post yoki insho yozish\n"
        "• Biznes, dasturlash va hayotiy g'oyalar berish\n"
        "• Muammolarni hal qilishda maslahatlar\n\n"
        "✍️ <i>Iltimos, o'z savolingiz yoki mavzuni yozib yuboring:</i>"
    )

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(
            text=text,
            reply_markup=get_back_button(),
            parse_mode="HTML"
        )
        await event.answer()
    else:
        await event.answer(
            text=text,
            reply_markup=get_back_button(),
            parse_mode="HTML"
        )


@ai_router.message(AIStates.waiting_for_prompt)
async def handle_ai_prompt(message: Message, state: FSMContext):
    """Foydalanuvchi yuborgan savolga AI orqali javob qaytarish"""
    if message.text and message.text.startswith("/"):
        # Agar buyruq kelsa (/start kabi), stateni tozalash
        await state.clear()
        return

    prompt = message.text.strip()
    await increment_user_requests(message.from_user.id)

    # Foydalanuvchiga bot o'ylanayotganini bildirish
    waiting_msg = await message.answer("🤖 <i>AI javob tayyorlamoqda, iltimos kuting...</i>", parse_mode="HTML")

    ai_response = await ask_ai(prompt)

    # Javob juda uzun bo'lsa Telegram limitiga moslash
    if len(ai_response) > 4000:
        ai_response = ai_response[:4000] + "\n\n... (matn qisqartirildi)"

    reply_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Yana savol berish", callback_data="menu_ai")],
            [InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="back_to_main")]
        ]
    )

    await waiting_msg.delete()
    await message.answer(
        text=f"🤖 <b>AI Yordamchi javobi:</b>\n\n{ai_response}",
        reply_markup=reply_keyboard,
        parse_mode="HTML"
    )
    await state.clear()
