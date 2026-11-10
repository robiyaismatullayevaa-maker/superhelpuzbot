"""
SUPER ASSISTANT - Asosiy Ishga Tushirish Fayli (main.py)
Muallif: Murodilova Robiya (@byrobiye)
Texnologiyalar: Python 3, aiogram 3, SQLite (aiosqlite)
"""
import os
import asyncio
import logging
import sys
from aiohttp import web

from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import StateFilter

# Sozlamalar va ma'lumotlar bazasi
from config import BOT_TOKEN, BOT_NAME, OWNER_NAME, OWNER_USERNAME, ADMIN_IDS
from database.db import init_db

# Handler routerlari
from handlers.start import start_router, handle_start
from handlers.ai_helper import ai_router
from handlers.weather import weather_router
from handlers.translator import translator_router
from handlers.calculator import calculator_router
from handlers.education import education_router
from handlers.reminders import reminders_router
from handlers.currency import currency_router
from handlers.admin import admin_router
from keyboards.inline import get_main_menu

# Logging sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)

# 10. Eng oxirgi Fallback (noto'g'ri xabarlar uchun) Router
fallback_router = Router()

@fallback_router.message(StateFilter("*"))
async def fallback_unknown_message_handler(message: Message, state: FSMContext):
    """Barcha boshqa noma'lum buyruq va matnlarni ushlovchi xavfsiz handler"""
    text = (message.text or "").strip().lower()

    if text.startswith("/start") or text == "start":
        await handle_start(message, state)
        return

    await state.clear()
    is_admin = message.from_user.id in ADMIN_IDS

    error_note = (
        "❓ <b>Kechirasiz, men bu buyruqni tushunmadim.</b>\n\n"
        "Iltimos, quyidagi menyudan kerakli xizmatni tanlang yoki /start buyrug'ini bosing:"
    )

    await message.answer(
        text=error_note,
        reply_markup=get_main_menu(is_admin),
        parse_mode="HTML"
    )


async def start_web_server():
    """Render.com bepul Web Service uchun HTTP server (Health Check)"""
    port = int(os.getenv("PORT", 0))
    if port > 0:
        async def ping_handler(request):
            return web.Response(text="SUPER ASSISTANT is alive and running 24/7! 🤖")

        app = web.Application()
        app.router.add_get("/", ping_handler)
        app.router.add_get("/health", ping_handler)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", port)
        await site.start()
        print(f"🌐 Render Web Service {port}-portda muvaffaqiyatli ishga tushdi.")


async def main():
    """Botni ishga tushiruvchi bosh funksiya"""
    print("=" * 60)
    print(f"🤖 {BOT_NAME} ishga tushirilmoqda...")
    print(f"👩‍💻 Muallif: {OWNER_NAME} (@{OWNER_USERNAME})")
    print("=" * 60)

    # 1. SQLite Ma'lumotlar Bazasini tayyorlash
    await init_db()
    print("✅ SQLite ma'lumotlar bazasi muvaffaqiyatli ishga tushirildi.")

    # 2. Render.com uchun web serverni yoqish (agar serverda bo'lsa)
    await start_web_server()

    # 3. Bot va Dispatcher yaratish
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # 4. Routerlarni tartib bilan ulash
    dp.include_router(start_router)
    dp.include_router(ai_router)
    dp.include_router(weather_router)
    dp.include_router(translator_router)
    dp.include_router(calculator_router)
    dp.include_router(education_router)
    dp.include_router(reminders_router)
    dp.include_router(currency_router)
    dp.include_router(admin_router)
    dp.include_router(fallback_router)

    print("\n🚀 SUPER ASSISTANT tayyor va xabarlarni kutmoqda! Telegramda /start bosing.\n")

    # 5. Yangi xabarlarni tinglash
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 Bot to'xtatildi!")
