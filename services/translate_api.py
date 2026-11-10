"""
SUPER ASSISTANT - Tarjimon Xizmati
Matnlarni o'zbek, rus, ingliz va boshqa tillarga tarjima qilish
"""
import aiohttp
import urllib.parse
import logging

LANG_NAMES = {
    "uz": "O'zbek tili 🇺🇿",
    "ru": "Rus tili 🇷🇺",
    "en": "Ingliz tili 🇬🇧",
    "tr": "Turk tili 🇹🇷",
    "ar": "Arab tili 🇸🇦",
    "de": "Nemis tili 🇩🇪"
}

async def translate_text(text: str, target_lang: str = "uz") -> dict:
    """Matnni avtomatik tildan mo'ljallangan tilga tarjima qilish"""
    encoded_text = urllib.parse.quote(text)
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={encoded_text}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status == 200:
                    data = await resp.json(content_type=None)
                    translated_chunks = []
                    if data and isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
                        for chunk in data[0]:
                            if chunk and len(chunk) > 0 and chunk[0]:
                                translated_chunks.append(chunk[0])
                        result = "".join(translated_chunks)
                        detected_lang = data[2] if len(data) > 2 and isinstance(data[2], str) else "auto"
                        return {
                            "success": True,
                            "original": text,
                            "translated": result,
                            "source_lang": detected_lang,
                            "target_lang": target_lang
                        }
    except Exception as e:
        logging.error(f"Google GTX tarjima xatolik: {e}")

    # Zaxira tarjima xizmati (MyMemory API)
    return await translate_mymemory(text, target_lang)

async def translate_mymemory(text: str, target_lang: str) -> dict:
    """MyMemory zaxira tarjima servisi"""
    try:
        url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(text)}&langpair=autodetect|{target_lang}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    res_text = data.get("responseData", {}).get("translatedText", "")
                    if res_text:
                        return {
                            "success": True,
                            "original": text,
                            "translated": res_text,
                            "source_lang": "auto",
                            "target_lang": target_lang
                        }
    except Exception as e:
        logging.error(f"MyMemory tarjima xatolik: {e}")

    return {
        "success": False,
        "original": text,
        "translated": "Kechirasiz, tarjima qilishda xatolik yuz berdi.",
        "source_lang": "auto",
        "target_lang": target_lang
    }
