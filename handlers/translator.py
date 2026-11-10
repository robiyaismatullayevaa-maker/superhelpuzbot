"""
SUPER ASSISTANT - Tarjimon Handleri
O'zbek, rus, ingliz va boshqa tillarga tarjima qilish
"""
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from utils.states import TranslateStates
from services.translate_api import translate_text, LANG_NAMES
from database.db import increment_user_requests
from keyboards.inline import get_translator_menu, get_back_button

translator_router = Router()

@translator_router.message(F.text == "🌍 Tarjimon", StateFilter("*"))
@translator_router.callback_query(F.data == "menu_translator", StateFilter("*"))
async def handle_translator_menu(event: Message | CallbackQuery, state: FSMContext):
    """Tarjimon bo'limini ochish va til tanlash"""
    await state.clear()
    await increment_user_requests(event.from_user.id)

    text = (
        "🌍 <b>Tarjimon Bo'limi</b>\n\n"
        "Matningizni qaysi tilga tarjima qilmoqchisiz?\n"
        "Quyidagi tillardan birini tanlang (yuborilayotgan til avtomatik aniqlanadi):"
    )

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(
            text=text,
            reply_markup=get_translator_menu(),
            parse_mode="HTML"
        )
        await event.answer()
    else:
        await event.answer(
            text=text,
            reply_markup=get_translator_menu(),
            parse_mode="HTML"
        )


@translator_router.callback_query(F.data.startswith("tr_to_"), StateFilter("*"))
async def handle_target_lang_choice(callback: CallbackQuery, state: FSMContext):
    """Tarjima qilinadigan til tanlanganda"""
    target_lang = callback.data.replace("tr_to_", "")
    await state.update_data(target_lang=target_lang)
    await state.set_state(TranslateStates.waiting_for_text)

    lang_title = LANG_NAMES.get(target_lang, target_lang)

    text = (
        f"🎯 Tanlangan til: <b>{lang_title}</b>\n\n"
        f"✍️ <i>Endi tarjima qilmoqchi bo'lgan so'z yoki matningizni yozib yuboring:</i>"
    )

    await callback.message.edit_text(
        text=text,
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await callback.answer()


@translator_router.message(TranslateStates.waiting_for_text)
async def handle_translation_input(message: Message, state: FSMContext):
    """Foydalanuvchi yuborgan matnni tarjima qilish"""
    if message.text and message.text.startswith("/"):
        await state.clear()
        return

    data = await state.get_data()
    target_lang = data.get("target_lang", "uz")
    user_text = message.text.strip()
    await increment_user_requests(message.from_user.id)

    waiting = await message.answer("🔄 <i>Tarjima qilinmoqda...</i>", parse_mode="HTML")

    result = await translate_text(user_text, target_lang=target_lang)
    lang_title = LANG_NAMES.get(target_lang, target_lang)

    res_msg = (
        f"🌍 <b>Tarjima Natijasi:</b>\n\n"
        f"📝 <b>Asl matn:</b>\n{result['original']}\n\n"
        f"🎯 <b>Tarjima ({lang_title}):</b>\n<b>{result['translated']}</b>"
    )

    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Yana matn tarjima qilish", callback_data=f"tr_to_{target_lang}")],
            [InlineKeyboardButton(text="🌐 Tilni o'zgartirish", callback_data="menu_translator")],
            [InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="back_to_main")]
        ]
    )

    await waiting.delete()
    await message.answer(
        text=res_msg,
        reply_markup=buttons,
        parse_mode="HTML"
    )
