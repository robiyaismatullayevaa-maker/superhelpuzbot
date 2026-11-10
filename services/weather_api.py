"""
SUPER ASSISTANT - Ob-havo Xizmati
Shahar nomi bo'yicha real ob-havoni aniqlash (wttr.in va Open-Meteo ochiq API lari)
"""
import aiohttp
import urllib.parse
import logging

WEATHER_ICONS = {
    "clear": "☀️ Ochiq havo",
    "sunny": "☀️ Quyoshli",
    "partly cloudy": "⛅ Qisman bulutli",
    "cloudy": "☁️ Bulutli",
    "overcast": "☁️ To'liq bulutli",
    "mist": "🌫 Tuman",
    "fog": "🌫 Qalin tuman",
    "light rain": "🌦 Yengil yomg'ir",
    "rain": "🌧 Yomg'ir",
    "heavy rain": "🌧 Kuchli yomg'ir",
    "snow": "🌨 Qor",
    "thunder": "⛈ Momaqaldiroq",
}

def translate_weather_desc(desc: str) -> str:
    desc_lower = desc.lower()
    for key, val in WEATHER_ICONS.items():
        if key in desc_lower:
            return val
    return f"🌤 {desc}"

async def get_weather(city_name: str) -> dict | None:
    """Shahar bo'yicha ob-havo ma'lumotlarini olish"""
    city_encoded = urllib.parse.quote(city_name.strip())
    url = f"https://wttr.in/{city_encoded}?format=j1"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status == 200:
                    data = await resp.json(content_type=None)
                    current = data.get("current_condition", [{}])[0]
                    area_info = data.get("nearest_area", [{}])[0]

                    area_name = area_info.get("areaName", [{}])[0].get("value", city_name)
                    country = area_info.get("country", [{}])[0].get("value", "")

                    temp_c = current.get("temp_C", "N/A")
                    feels_like = current.get("FeelsLikeC", "N/A")
                    humidity = current.get("humidity", "N/A")
                    wind_kmph = current.get("windspeedKmph", "N/A")
                    wind_dir = current.get("winddir16Point", "")
                    weather_desc = current.get("weatherDesc", [{}])[0].get("value", "Nomalum")
                    pressure = current.get("pressure", "N/A")

                    return {
                        "city": area_name,
                        "country": country,
                        "temp": temp_c,
                        "feels_like": feels_like,
                        "humidity": humidity,
                        "wind_speed": wind_kmph,
                        "wind_dir": wind_dir,
                        "desc": translate_weather_desc(weather_desc),
                        "pressure": pressure
                    }
    except Exception as e:
        logging.error(f"wttr.in xatolik: {e}")

    # Agar wttr.in ishlamasa, Open-Meteo zaxira tizimi:
    return await get_weather_openmeteo(city_name)

async def get_weather_openmeteo(city_name: str) -> dict | None:
    """Open-Meteo zaxira ob-havo xizmati"""
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(city_name)}&count=1&language=uz&format=json"
        async with aiohttp.ClientSession() as session:
            async with session.get(geo_url, timeout=aiohttp.ClientTimeout(total=6)) as g_resp:
                if g_resp.status == 200:
                    g_data = await g_resp.json()
                    results = g_data.get("results")
                    if not results:
                        return None
                    loc = results[0]
                    lat, lon = loc["latitude"], loc["longitude"]
                    name = loc.get("name", city_name)
                    country = loc.get("country", "")

                    w_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m"
                    async with session.get(w_url, timeout=aiohttp.ClientTimeout(total=6)) as w_resp:
                        if w_resp.status == 200:
                            w_data = await w_resp.json()
                            curr = w_data.get("current", {})
                            temp = curr.get("temperature_2m", "0")
                            feels = curr.get("apparent_temperature", "0")
                            hum = curr.get("relative_humidity_2m", "0")
                            wind = curr.get("wind_speed_10m", "0")
                            return {
                                "city": name,
                                "country": country,
                                "temp": temp,
                                "feels_like": feels,
                                "humidity": hum,
                                "wind_speed": wind,
                                "wind_dir": "",
                                "desc": "🌤 Ochiq/O'zgaruvchan havo",
                                "pressure": "760"
                            }
    except Exception as e:
        logging.error(f"Open-Meteo xatolik: {e}")
    return None

def format_weather_text(data: dict) -> str:
    """Ob-havo ma'lumotlarini chiroyli formatda chiqarish"""
    if not data:
        return "⚠️ Shahar topilmadi yoki ma'lumot olishda xatolik yuz berdi. Shahar nomini to'g'ri yozganingizga ishonch hosil qiling (masalan: <i>Toshkent</i>, <i>Samarqand</i>, <i>Buxoro</i>)."

    text = (
        f"🌤 <b>{data['city']} ({data['country']}) ob-havo ma'lumotlari:</b>\n\n"
        f"🌡 Harorat: <b>{data['temp']}°C</b> (sezilishi: <b>{data['feels_like']}°C</b>)\n"
        f"📋 Holat: <b>{data['desc']}</b>\n"
        f"💧 Namlik: <b>{data['humidity']}%</b>\n"
        f"💨 Shamol tezligi: <b>{data['wind_speed']} km/soat</b> {data['wind_dir']}\n"
        f"🧭 Atmosfera bosimi: <b>{data['pressure']} hPa</b>\n\n"
        f"💡 <i>Boshqa shahar ob-havosini bilish uchun shahar nomini yuborishingiz mumkin.</i>"
    )
    return text
