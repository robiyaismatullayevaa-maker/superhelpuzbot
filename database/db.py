"""
SUPER ASSISTANT - SQLite Ma'lumotlar Bazasi Moduli
Foydalanuvchilar, eslatmalar va statistikani xavfsiz saqlash
"""
import aiosqlite
from datetime import datetime
from config import DB_PATH, ADMIN_IDS

async def init_db():
    """Baza jadvallarini yaratish"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Foydalanuvchilar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT,
                username TEXT,
                joined_at TEXT,
                requests_count INTEGER DEFAULT 0,
                is_admin INTEGER DEFAULT 0
            )
        """)
        # Eslatmalar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                text TEXT,
                remind_time TEXT,
                is_done INTEGER DEFAULT 0,
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        await db.commit()

async def add_or_update_user(user_id: int, full_name: str, username: str | None = None):
    """Foydalanuvchini bazaga qo'shish yoki yangilash"""
    is_admin = 1 if user_id in ADMIN_IDS else 0
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT user_id, is_admin FROM users WHERE user_id = ?", (user_id,))
        user = await cursor.fetchone()
        if user:
            # Agar oldin bo'lsa ma'lumotlarini yangilaymiz
            await db.execute(
                "UPDATE users SET full_name = ?, username = ? WHERE user_id = ?",
                (full_name, username or "", user_id)
            )
        else:
            # Yangi foydalanuvchi
            await db.execute(
                "INSERT INTO users (user_id, full_name, username, joined_at, requests_count, is_admin) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, full_name, username or "", now, 0, is_admin)
            )
        await db.commit()

async def increment_user_requests(user_id: int):
    """Foydalanuvchi qilgan so'rovlar hisoblagichini oshirish"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE users SET requests_count = requests_count + 1 WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()

async def get_user(user_id: int):
    """Bitta foydalanuvchi ma'lumotlarini olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return await cursor.fetchone()

async def get_all_users():
    """Barcha foydalanuvchilar ro'yxatini olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users")
        return await cursor.fetchall()

async def get_total_users_count() -> int:
    """Foydalanuvchilar umumiy sonini olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        row = await cursor.fetchone()
        return row[0] if row else 0

async def get_total_requests_count() -> int:
    """Jami so'rovlar sonini olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT SUM(requests_count) FROM users")
        row = await cursor.fetchone()
        return row[0] if (row and row[0] is not None) else 0

# ==================== ESLATMALAR BO'LIMI ====================

async def add_reminder(user_id: int, text: str, remind_time: str) -> int:
    """Yangi eslatma qo'shish"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO reminders (user_id, text, remind_time, is_done, created_at) VALUES (?, ?, ?, 0, ?)",
            (user_id, text, remind_time, now)
        )
        await db.commit()
        return cursor.lastrowid

async def get_user_reminders(user_id: int):
    """Foydalanuvchining barcha eslatmalarini olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM reminders WHERE user_id = ? ORDER BY id DESC",
            (user_id,)
        )
        return await cursor.fetchall()

async def delete_reminder(reminder_id: int, user_id: int) -> bool:
    """Eslatmani o'chirish"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "DELETE FROM reminders WHERE id = ? AND user_id = ?",
            (reminder_id, user_id)
        )
        await db.commit()
        return cursor.rowcount > 0

async def toggle_reminder_status(reminder_id: int, user_id: int):
    """Eslatma holatini o'zgartirish (bajarildi / bajarilmadi)"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "UPDATE reminders SET is_done = CASE WHEN is_done = 1 THEN 0 ELSE 1 END WHERE id = ? AND user_id = ?",
            (reminder_id, user_id)
        )
        await db.commit()
        return cursor.rowcount > 0
