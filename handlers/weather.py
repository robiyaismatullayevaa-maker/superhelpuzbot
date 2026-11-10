"""
SUPER ASSISTANT - Ob-havo Handleri
Shahar bo'yicha real ob-havo ma'lumotlari
"""
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from utils.states import WeatherStates
from services.weather_api import get_weather, format_weather_text
from database.db import increment_user_requests
from keyboards.inline import get_weather_menu, get_back_button

weather_router = Router()

@weather_router.message(F.text == "🌤 Ob-havo", StateFilter("*"))
@weather_router.callback_query(F.data == "menu_weather", StateFilter("*"))
async def handle_weather_menu(event: Message | CallbackQuery, state: FSMContext):
    """Ob-havo bo'limini ochish"""
    await state.clear()
    await increment_user_requests(event.from_user.id)

    text = (
        "🌤 <b>Ob-havo Bo'limi</b>\n\n"
        "Quyidagi shaharlardan birini tanlang yoki o'zingiz istagan shahar nomini kiriting:"
    )

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(
            text=text,
            reply_markup=get_weather_menu(),
            parse_mode="HTML"
        )
        await event.answer()
    else:
        await event.answer(
            text=text,
            reply_markup=get_weather_menu(),
            parse_mode="HTML"
        )


@weather_router.callback_query(F.data.startswith("weather_city_"), StateFilter("*"))
async def handle_quick_city(callback: CallbackQuery):
    """Tayyor shahar tugmasi bosilganda"""
    city_name = callback.data.replace("weather_city_", "")
    await increment_user_requests(callback.from_user.id)

    await callback.message.edit_text(f"⏳ <i>{city_name} ob-havosi yuklanmoqda...</i>", parse_mode="HTML")

    weather_data = await get_weather(city_name)
    result_text = format_weather_text(weather_data)

    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Yangilash", callback_data=f"weather_city_{city_name}")],
            [InlineKeyboardButton(text="🌤 Boshqa shahar", callback_data="menu_weather")],
            [InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="back_to_main")]
        ]
    )

    await callback.message.edit_text(
        text=result_text,
        reply_markup=buttons,
        parse_mode="HTML"
    )
    await callback.answer()


@weather_router.callback_query(F.data == "weather_custom", StateFilter("*"))
async def handle_custom_city_request(callback: CallbackQuery, state: FSMContext):
    """Boshqa shahar yozish rejimiga o'tish"""
    await state.set_state(WeatherStates.waiting_for_city)
    await callback.message.edit_text(
        text="✍️ <b>Istalgan shahar nomini yozib yuboring:</b>\n<i>(Masalan: Andijon, Namangan, Xiva, Istanbul, Moskva...)</i>",
        reply_markup=get_back_button(),
        parse_mode="HTML"
    )
    await callback.answer()


@weather_router.message(WeatherStates.waiting_for_city)
async def handle_custom_city_input(message: Message, state: FSMContext):
    """Foydalanuvchi yozgan shahar ob-havosini ko'rsatish"""
    if message.text and message.text.startswith("/"):
        await state.clear()
        return

    city_name = message.text.strip()
    await increment_user_requests(message.from_user.id)

    waiting = await message.answer("⏳ <i>Ob-havo ma'lumotlari olinmoqda...</i>", parse_mode="HTML")

    weather_data = await get_weather(city_name)
    result_text = format_weather_text(weather_data)

    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌤 Boshqa shahar", callback_data="menu_weather")],
            [InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="back_to_main")]
        ]
    )

    await waiting.delete()
    await message.answer(
        text=result_text,
        reply_markup=buttons,
        parse_mode="HTML"
    )
    await state.clear()
