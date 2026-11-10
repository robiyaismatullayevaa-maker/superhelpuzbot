# 🌟 SUPER ASSISTANT — Professional Telegram Bot

Ushbu bot **Python**, **aiogram 3** va **SQLite** asosida yaratilgan ko'p funksiyali shaxsiy yordamchi botdir.

👩‍💻 **Loyiha muallifi:** Murodilova Robiya ([@byrobiye](https://t.me/byrobiye))  
🤖 **Bot nomi:** SUPER ASSISTANT  

---

## 🚀 Asosiy Imkoniyatlar (9 ta Bo'lim)

1. 🤖 **AI Yordamchi:** Har qanday savollarga javob berish, matnlar yozish, biznes va hayotiy g'oyalar berish.
2. 🌤 **Ob-havo:** Toshkent, Samarqand va dunyoning barcha shaharlari bo'yicha harorat, namlik, shamol va atmosfera bosimini real vaqtda ko'rsatish.
3. 🌍 **Tarjimon:** O'zbek, Rus, Ingliz va Turk tillariga avtomatik tilni aniqlagan holda yuqori aniqlikda tarjima qilish.
4. 🧮 **Kalkulyator:** Matematik ifodalarni xavfsiz hisoblash va har qanday summaning foiz stavkasini aniqlash.
5. 📚 **Ta'lim:** Ingliz tili yangi so'zlari (kun so'zi), 4 ta variantli interaktiv viktorina (testlar), foydali iboralar va qiziqarli ilmiy faktlar.
6. 📝 **Eslatmalar:** Vazifalar ro'yxatini rejalashtirish, vaqt belgilash, bajarilgan deb belgilash va o'chirish. Ma'lumotlar xavfsiz **SQLite** bazasida saqlanadi.
7. 💱 **Valyuta Kursi:** O'zbekiston Respublikasi Markaziy Banki rasmiy kursi (USD, EUR, RUB va b.) hamda valyuta konvertori.
8. 👤 **Foydalanuvchi Profili:** Telegram ID, ism, ro'yxatdan o'tgan sana va botdan foydalanish statistikasi.
9. 👨‍💻 **Admin Panel:** Foydalanuvchilar soni, umumiy so'rovlar statistikasi va barcha foydalanuvchilarga xabar tarqatish (Broadcast).

---

## 📁 Loyiha Tuzilmasi

```text
yangi bot/
├── database/
│   └── db.py            # SQLite ma'lumotlar bazasi (aiosqlite)
├── handlers/
│   ├── start.py         # /start, asosiy menyu va profil
│   ├── ai_helper.py     # AI yordamchi
│   ├── weather.py       # Ob-havo
│   ├── translator.py    # Tarjimon
│   ├── calculator.py    # Kalkulyator va foiz
│   ├── education.py     # Ta'lim, testlar va faktlar
│   ├── reminders.py     # Eslatmalar va vazifalar
│   ├── currency.py      # Markaziy Bank kurslari
│   └── admin.py         # Admin panel
├── keyboards/
│   └── inline.py        # Chiroyli Inline tugmalar
├── services/
│   ├── ai_service.py    # AI xizmati
│   ├── weather_api.py   # Ob-havo ochiq API
│   ├── translate_api.py # Tarjima ochiq API
│   └── currency_api.py  # CBU valyuta API
├── utils/
│   └── states.py        # FSM holatlari
├── config.py            # Token, adminlar va muallif ma'lumotlari
├── main.py              # Asosiy ishga tushirish fayli
├── requirements.txt     # Kerakli kutubxonalar
└── start_bot.bat        # 1 ta bosishda botni yoqish
```

---

## 🛠 Ishga tushirish:

Loyiha papkasidagi **`start_bot.bat`** fayli ustiga sichqoncha bilan 2 marta bosing!
Bot avtomatik ishga tushadi va Telegramda **/start** bosib foydalanishingiz mumkin.
