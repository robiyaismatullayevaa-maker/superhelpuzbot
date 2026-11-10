"""
SUPER ASSISTANT - Markaziy Bank Valyuta Kurslari Xizmati
O'zbekiston Respublikasi Markaziy Banki (CBU) rasmiy ochiq API si
"""
import aiohttp
import logging

CBU_API_URL = "https://cbu.uz/oz/arkhiv-kursov-valyut/json/"

# Asosiy kuzatiladigan valyutalar
MAIN_CURRENCIES = ["USD", "EUR", "RUB", "KZT", "GBP", "TRY", "CNY", "KRW", "AED"]

async def get_currency_rates():
    """Barcha asosiy valyutalar kursini olish"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(CBU_API_URL, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    rates = {}
                    for item in data:
                        ccy = item.get("Ccy")
                        if ccy:
                            rates[ccy] = {
                                "code": ccy,
                                "name": item.get("CcyNm_UZ", ccy),
                                "rate": float(item.get("Rate", 0)),
                                "diff": item.get("Diff", "0"),
                                "date": item.get("Date", "")
                            }
                    return rates
    except Exception as e:
        logging.error(f"Valyuta kurslarini olishda xatolik: {e}")
    return None

def format_currency_text(rates: dict) -> str:
    """Valyutalar kursini chiroyli matn ko'rinishida formatlash"""
    if not rates:
        return "⚠️ Valyuta kurslarini olishda xatolik yuz berdi. Keyinroq qayta urinib ko'ring."

    # Sana
    sample_date = rates.get("USD", {}).get("date", "")
    text = (
        f"🏦 <b>O'zbekiston Markaziy Banki rasmiy valyuta kurslari:</b>\n"
        f"📅 Sana: <b>{sample_date}</b>\n\n"
    )

    icons = {
        "USD": "🇺🇸",
        "EUR": "🇪🇺",
        "RUB": "🇷🇺",
        "KZT": "🇰🇿",
        "GBP": "🇬🇧",
        "TRY": "🇹🇷",
        "CNY": "🇨🇳",
        "KRW": "🇰🇷",
        "AED": "🇦🇪"
    }

    for ccy in MAIN_CURRENCIES:
        if ccy in rates:
            item = rates[ccy]
            icon = icons.get(ccy, "💱")
            diff = item['diff']
            diff_sign = "📈 +" if not diff.startswith("-") and diff != "0" else ("📉 " if diff.startswith("-") else "➖ ")
            text += f"{icon} <b>1 {ccy}</b> ({item['name']}) = <b>{item['rate']:,.2f} UZS</b> ({diff_sign}{diff})\n"

    text += "\n💡 <i>Valyutani so'mga yoki so'mni chet el valyutasiga hisoblash uchun quyidagi 'Valyuta hisoblash' tugmasidan foydalaning.</i>"
    return text

def convert_currency(amount: float, from_ccy: str, to_ccy: str, rates: dict) -> str:
    """Valyutani konvertatsiya qilish"""
    if not rates:
        return "⚠️ Valyuta kurslari ma'lumoti mavjud emas."

    from_ccy = from_ccy.upper()
    to_ccy = to_ccy.upper()

    # UZS dan chet el valyutasiga
    if from_ccy == "UZS" and to_ccy in rates:
        target_rate = rates[to_ccy]["rate"]
        res = amount / target_rate
        return f"💱 <b>{amount:,.0f} UZS</b> = <b>{res:,.2f} {to_ccy}</b>\n(Kurs: 1 {to_ccy} = {target_rate:,.2f} UZS)"

    # Chet el valyutasidan UZS ga
    elif from_ccy in rates and to_ccy == "UZS":
        source_rate = rates[from_ccy]["rate"]
        res = amount * source_rate
        return f"💱 <b>{amount:,.2f} {from_ccy}</b> = <b>{res:,.0f} UZS</b>\n(Kurs: 1 {from_ccy} = {source_rate:,.2f} UZS)"

    # Ikkita chet el valyutasi o'rtasida
    elif from_ccy in rates and to_ccy in rates:
        source_rate = rates[from_ccy]["rate"]
        target_rate = rates[to_ccy]["rate"]
        in_uzs = amount * source_rate
        res = in_uzs / target_rate
        return f"💱 <b>{amount:,.2f} {from_ccy}</b> = <b>{res:,.2f} {to_ccy}</b>"

    return "⚠️ Noto'g'ri valyuta kodi kiritildi."
