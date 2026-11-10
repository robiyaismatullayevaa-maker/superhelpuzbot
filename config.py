"""
SUPER ASSISTANT - Sozlamalar va Konfiguratsiya fayli
Muallif: Murodilova Robiya (@byrobiye)
"""
import os
from dotenv import load_dotenv

# .env faylini yuklash (agar mavjud bo'lsa)
load_dotenv()

# Telegram Bot API Token
# Serverda yoki lokalda .env orqali yoki to'g'ridan-to'g'ri o'qiladi
BOT_TOKEN = os.getenv("BOT_TOKEN", "9144030981:AAE1o6TAc8dBuJWiZEnV5SKNaGjBZN-iu48")

# Bot egasi va aloqa ma'lumotlari
BOT_NAME = "SUPER ASSISTANT"
OWNER_NAME = "Murodilova Robiya"
OWNER_USERNAME = "byrobiye"  # @ belgisiz

# Bot Administratorlari (Telegram ID lar ro'yxati)
ADMIN_IDS = [
    9144030981,   # Asosiy admin
]

# SQLite ma'lumotlar bazasi fayli
DB_PATH = os.getenv("DB_PATH", "database/database.db")
