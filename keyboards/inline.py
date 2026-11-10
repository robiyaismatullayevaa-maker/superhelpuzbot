"""
SUPER ASSISTANT - Inline Klaviaturalar (Tugmalar)
Muallif: Murodilova Robiya (@byrobiye)
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import OWNER_USERNAME, OWNER_NAME

def get_main_menu(is_admin: bool = False) -> InlineKeyboardMarkup:
    """Asosiy menyu tugmalari"""
    keyboard = [
        [
            InlineKeyboardButton(text="🤖 AI Yordamchi", callback_data="menu_ai"),
            InlineKeyboardButton(text="🌤 Ob-havo", callback_data="menu_weather")
        ],
        [
            InlineKeyboardButton(text="🌍 Tarjimon", callback_data="menu_translator"),
            InlineKeyboardButton(text="🧮 Kalkulyator", callback_data="menu_calculator")
        ],
        [
            InlineKeyboardButton(text="📚 Ta'lim", callback_data="menu_education"),
            InlineKeyboardButton(text="📝 Eslatmalar", callback_data="menu_reminders")
        ],
        [
            InlineKeyboardButton(text="💱 Valyuta kursi", callback_data="menu_currency"),
            InlineKeyboardButton(text="👤 Profil", callback_data="menu_profile")
        ],
        [
            InlineKeyboardButton(text="📞 Bog'lanish (Robiya)", url=f"https://t.me/{OWNER_USERNAME}")
        ]
    ]

    if is_admin:
        keyboard.append([
            InlineKeyboardButton(text="👨‍💻 Admin Panel", callback_data="menu_admin")
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_back_button() -> InlineKeyboardMarkup:
    """Orqaga qaytish tugmasi"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Asosiy menyuga qaytish", callback_data="back_to_main")]
        ]
    )


def get_weather_menu() -> InlineKeyboardMarkup:
    """Ob-havo bo'limi tugmalari"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 Toshkent", callback_data="weather_city_Toshkent"),
                InlineKeyboardButton(text="🇺🇿 Samarqand", callback_data="weather_city_Samarqand")
            ],
            [
                InlineKeyboardButton(text="🇺🇿 Farg'ona", callback_data="weather_city_Farg'ona"),
                InlineKeyboardButton(text="🇺🇿 Buxoro", callback_data="weather_city_Buxoro")
            ],
            [
                InlineKeyboardButton(text="✏️ Boshqa shahar yozish", callback_data="weather_custom")
            ],
            [
                InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="back_to_main")
            ]
        ]
    )


def get_translator_menu() -> InlineKeyboardMarkup:
    """Tarjimon tili tanlash tugmalari"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 O'zbek tiliga", callback_data="tr_to_uz"),
                InlineKeyboardButton(text="🇷🇺 Rus tiliga", callback_data="tr_to_ru")
            ],
            [
                InlineKeyboardButton(text="🇬🇧 Ingliz tiliga", callback_data="tr_to_en"),
                InlineKeyboardButton(text="🇹🇷 Turk tiliga", callback_data="tr_to_tr")
            ],
            [
                InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="back_to_main")
            ]
        ]
    )


def get_calculator_menu() -> InlineKeyboardMarkup:
    """Kalkulyator bo'limi tugmalari"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🧮 Matematik ifoda hisoblash", callback_data="calc_expr"),
            ],
            [
                InlineKeyboardButton(text="📊 Foiz hisoblash", callback_data="calc_percent")
            ],
            [
                InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="back_to_main")
            ]
        ]
    )


def get_education_menu() -> InlineKeyboardMarkup:
    """Ta'lim bo'limi menyusi"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📖 Kun so'zi (Ingliz tili)", callback_data="edu_word"),
                InlineKeyboardButton(text="🎯 Test topshirish", callback_data="edu_quiz")
            ],
            [
                InlineKeyboardButton(text="🧠 Qiziqarli fakt", callback_data="edu_fact"),
                InlineKeyboardButton(text="📚 Top so'zlar", callback_data="edu_top_words")
            ],
            [
                InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="back_to_main")
            ]
        ]
    )


def get_reminders_menu() -> InlineKeyboardMarkup:
    """Eslatmalar menyusi"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ Yangi eslatma qo'shish", callback_data="remind_add")
            ],
            [
                InlineKeyboardButton(text="📋 Barcha eslatmalarim", callback_data="remind_list")
            ],
            [
                InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="back_to_main")
            ]
        ]
    )


def get_currency_menu() -> InlineKeyboardMarkup:
    """Valyuta kursi menyusi"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 Kurslarni yangilash", callback_data="curr_refresh"),
                InlineKeyboardButton(text="💱 Konvertor", callback_data="curr_convert")
            ],
            [
                InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="back_to_main")
            ]
        ]
    )


def get_admin_menu() -> InlineKeyboardMarkup:
    """Admin panel menyusi"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Batafsil statistika", callback_data="admin_stats"),
            ],
            [
                InlineKeyboardButton(text="📢 Foydalanuvchilarga xabar yuborish", callback_data="admin_broadcast")
            ],
            [
                InlineKeyboardButton(text="⬅️ Asosiy menyu", callback_data="back_to_main")
            ]
        ]
    )
