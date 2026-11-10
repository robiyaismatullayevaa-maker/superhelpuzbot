"""
SUPER ASSISTANT - AI Yordamchi Xizmati
Savollarga javob berish, matn yozish, g'oyalar berish
"""
import aiohttp
import urllib.parse
import logging

SYSTEM_PROMPT = (
    "Sen Telegramdagi 'SUPER ASSISTANT' boti yordamchisisan. "
    "Foydalanuvchining savollariga o'zbek tilida juda chiroyli, muloyim, aniq va foydali javob ber. "
    "Agar matn yozishni so'rasa, professional darajada yoz. "
    "Agar biznes yoki loyiha g'oyalarini so'rasa, original va qiziqarli g'oyalarni taqdim et."
)

async def ask_ai(prompt: str) -> str:
    """AI modelidan javob olish (Pollinations AI ochiq bepul API)"""
    try:
        encoded_system = urllib.parse.quote(SYSTEM_PROMPT)
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://text.pollinations.ai/{encoded_prompt}?system={encoded_system}&model=openai"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                if resp.status == 200:
                    answer = await resp.text()
                    if answer and len(answer.strip()) > 0:
                        return answer.strip()
    except Exception as e:
        logging.error(f"AI API xatolik: {e}")

    # Zaxira intellektual javob tizimi:
    return generate_fallback_ai_response(prompt)

def generate_fallback_ai_response(prompt: str) -> str:
    """Internet sekinlashganda yoki API vaqtincha javob bermaganda ishlaydigan aqlli zaxira javob"""
    p_lower = prompt.lower()

    if any(w in p_lower for w in ["salom", "assalomu", "qalesan", "qalaysiz"]):
        return (
            "Assalomu alaykum! Men sizning AI yordamchingizman. 😊\n"
            "Sizga har qanday mavzuda matn yozish, g'oyalar berish yoki savollaringizga javob berishda bajonidil yordam beraman! Savolingizni yozing."
        )

    if any(w in p_lower for w in ["g'oya", "goya", "biznes", "loyiha", "startup"]):
        return (
            "💡 <b>Siz uchun ajoyib g'oyalar:</b>\n\n"
            "1. <b>Telegram Mini App (Do'kon yoki Xizmatlar):</b> Hozirgi kunda bizneslar uchun Telegram ichida ishlovchi do'konlar juda ommabop.\n"
            "2. <b>AI Content Studio:</b> Ijtimoiy tarmoqlar uchun AI yordamida postlar, ssenariylar va dizayn matnlari tayyorlash xizmati.\n"
            "3. <b>Shaxsiy ta'lim yoki til o'rganish kursi:</b> Telegram orqali mikro-darslar va interaktiv testlar.\n"
            "4. <b>Yetkazib berish va logistika agregatori:</b> Mahalliy mahsulotlarni tezkor yetkazib berish servisi."
        )

    if any(w in p_lower for w in ["matn", "maqola", "post", "tabrik", "xat"]):
        return (
            "📝 <b>Matn yozish bo'yicha maslahat va shablon:</b>\n\n"
            "Matningiz jozibali bo'lishi uchun 3 ta asosiy qoidaga e'tibor bering:\n"
            "1. <b>Diqqatni jalb qiluvchi sarlavha (Hook):</b> Birinchi 2 qatorda asosiy qiziqishni uyg'oting.\n"
            "2. <b>Asosiy qiymat (Value):</b> O'quvchi bu matndan qanday foyda yoki xulosa olishini aniq yozing.\n"
            "3. <b>Harakatga chaqiruv (Call to Action):</b> Oxirida savol bering yoki taklif qiling."
        )

    return (
        f"🤖 <b>AI Yordamchi tahlili:</b>\n\n"
        f"Sizning savolingiz: <i>'{prompt}'</i>\n\n"
        "Ushbu mavzu bo'yicha tavsiyalar:\n"
        "• Masalani kichik bo'laklarga ajratib rejalashtiring.\n"
        "• Eng muhim va ustuvor qadamdan boshlang.\n"
        "• Qo'shimcha aniq savol bering, batafsil tushuntirib beraman!"
    )
