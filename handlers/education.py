"""
SUPER ASSISTANT - Ta'lim Handleri
Ingliz tili, testlar, lug'at va qiziqarli faktlar
"""
import random
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from database.db import increment_user_requests
from keyboards.inline import get_education_menu, get_back_button

education_router = Router()

# 1. Kun so'zlari bazasi
VOCABULARY = [
    {
        "word": "Perseverance",
        "transcription": "[ˌpɜː.sɪˈvɪə.rəns]",
        "translation": "Sabr-toqat, matonat, tirishqoqlik",
        "example": "Through hard work and perseverance, she succeeded.",
        "example_tr": "Mehnat va matonat orqali u muvaffaqiyatga erishdi."
    },
    {
        "word": "Magnificent",
        "transcription": "[mæɡˈnɪf.ɪ.sənt]",
        "translation": "Muhtasham, ajoyib, ko'rkam",
        "example": "The view from the top of the mountain was magnificent.",
        "example_tr": "Tog' cho'qqisidan ko'rinish muhtasham edi."
    },
    {
        "word": "Opportunity",
        "transcription": "[ˌɒp.əˈtʃuː.nə.ti]",
        "translation": "Imkoniyat, qulay fursat",
        "example": "Do not miss this wonderful opportunity.",
        "example_tr": "Bu ajoyib imkoniyatni qo'ldan boy bermang."
    },
    {
        "word": "Curiosity",
        "transcription": "[ˌkjʊə.riˈɒs.ə.ti]",
        "translation": "Qiziquvchanlik, qiziqish",
        "example": "Children have a natural curiosity about the world.",
        "example_tr": "Bolalarda dunyoga nisbatan tabiiy qiziquvchanlik bo'ladi."
    },
    {
        "word": "Resilient",
        "transcription": "[rɪˈzɪl.jənt]",
        "translation": "Chidamli, egilmas, tez tiklanuvchan",
        "example": "She is resilient and never gives up easily.",
        "example_tr": "U juda chidamli va hech qachon osonlikcha taslim bo'lmaydi."
    },
    {
        "word": "Accomplish",
        "transcription": "[əˈkʌm.plɪʃ]",
        "translation": "Amalga oshirmoq, uddalamoq",
        "example": "You can accomplish anything if you believe in yourself.",
        "example_tr": "O'zingizga ishonsangiz, har qanday narsani amalga oshira olasiz."
    }
]

# 2. Interaktiv Testlar (Quiz)
QUIZ_QUESTIONS = [
    {
        "id": 1,
        "question": "'Courage' so'zining ma'nosi nima?",
        "options": ["Jasorat, qo'rqmaslik", "Qo'rquv", "G'amginlik", "Charchoq"],
        "correct": 0
    },
    {
        "id": 2,
        "question": "'To invent' fe'li qanday tarjima qilinadi?",
        "options": ["Sotib olmoq", "Ixtiro qilmoq", "Yo'qotmoq", "Tinglamoq"],
        "correct": 1
    },
    {
        "id": 3,
        "question": "Qaysi so'z 'Muvaffaqiyat' ma'nosini beradi?",
        "options": ["Failure", "Patience", "Success", "Mistake"],
        "correct": 2
    },
    {
        "id": 4,
        "question": "'Environment' so'zi nimani anglatadi?",
        "options": ["Atrof-muhit", "Ob-havo", "Sayohat", "Texnologiya"],
        "correct": 0
    },
    {
        "id": 5,
        "question": "'Valuable' so'zining ma'nosi:",
        "options": ["Arzon", "Qimmatbaho, qadrli", "Qiyin", "Xavfli"],
        "correct": 1
    }
]

# 3. Qiziqarli Faktlar
FACTS = [
    "🧠 Inson miyasi tunda kunduzgidan ko'ra faolroq ishlaydi va uyqu paytida yangi ma'lumotlarni tartibga soladi.",
    "🍯 Asal yer yuzidagi buzilmaydigan yagona oziq-ovqat hisoblanadi. Misr piramidalaridan topilgan 3000 yillik asal hali ham yaroqli chiqqan!",
    "🐙 Sakkizoyoqning (osminog) 3 ta yuragi va ko'k rangli qoni bor.",
    "🌍 Yer yuzidagi kislorodning 70% dan ortig'i okeandagi fitoplanktonlar tomonidan ishlab chiqariladi, o'rmonlar tomonidan emas.",
    "⚡️ Bitta chaqmoq chaqnashi quyosh sirtidan 5 barobar issiqroq (taxminan 30,000°C) harorat hosil qiladi.",
    "📱 Zamonaviy oddiy smartfon kompyuteri 1969-yilda oyni zabt etgan Apollo 11 kosmik kemasi kompyuteridan million barobar kuchliroqdir."
]


@education_router.message(F.text == "📚 Ta'lim", StateFilter("*"))
@education_router.callback_query(F.data == "menu_education", StateFilter("*"))
async def handle_education_menu(event: Message | CallbackQuery, state: FSMContext):
    """Ta'lim bo'limini ochish"""
    await state.clear()
    await increment_user_requests(event.from_user.id)

    text = (
        "📚 <b>Ta'lim va Rivojlanish Bo'limi</b>\n\n"
        "Bilimingizni oshirish uchun quyidagi bo'limlardan birini tanlang:\n\n"
        "• <b>Kun so'zi:</b> Yangi inglizcha so'z, transkripsiya va misollar\n"
        "• <b>Test topshirish:</b> Ingliz tili bo'yicha interaktiv viktorina\n"
        "• <b>Qiziqarli fakt:</b> Dunyo va fan mo'jizalari\n"
        "• <b>Top so'zlar:</b> Eng muhim so'zlar ro'yxati"
    )

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(
            text=text,
            reply_markup=get_education_menu(),
            parse_mode="HTML"
        )
        await event.answer()
    else:
        await event.answer(
            text=text,
            reply_markup=get_education_menu(),
            parse_mode="HTML"
        )


@education_router.callback_query(F.data == "edu_word", StateFilter("*"))
async def handle_edu_word(callback: CallbackQuery):
    """Tasodifiy kun so'zini chiqarish"""
    await increment_user_requests(callback.from_user.id)
    item = random.choice(VOCABULARY)

    text = (
        f"📖 <b>Bugungi Yangi So'z:</b>\n\n"
        f"🔤 So'z: <b>{item['word']}</b> {item['transcription']}\n"
        f"🇺🇿 Tarjimasi: <b>{item['translation']}</b>\n\n"
        f"📝 <b>Misol:</b>\n"
        f"🇬🇧 <i>{item['example']}</i>\n"
        f"🇺🇿 <i>{item['example_tr']}</i>"
    )

    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Boshqa so'z", callback_data="edu_word")],
            [InlineKeyboardButton(text="🎯 Test ishlash", callback_data="edu_quiz")],
            [InlineKeyboardButton(text="⬅️ Ta'lim menyusi", callback_data="menu_education")]
        ]
    )

    await callback.message.edit_text(text=text, reply_markup=buttons, parse_mode="HTML")
    await callback.answer()


@education_router.callback_query(F.data == "edu_quiz", StateFilter("*"))
async def handle_edu_quiz(callback: CallbackQuery):
    """Interaktiv test savolini chiqarish"""
    await increment_user_requests(callback.from_user.id)
    quiz_idx = random.randint(0, len(QUIZ_QUESTIONS) - 1)
    q = QUIZ_QUESTIONS[quiz_idx]

    text = (
        f"🎯 <b>Ingliz tili testi:</b>\n\n"
        f"❓ <b>Savol:</b> {q['question']}\n\n"
        f"<i>To'g'ri javobni tanlang:</i>"
    )

    buttons_list = []
    for opt_idx, opt_text in enumerate(q["options"]):
        buttons_list.append([
            InlineKeyboardButton(text=f"▫️ {opt_text}", callback_data=f"quiz_{quiz_idx}_{opt_idx}")
        ])

    buttons_list.append([InlineKeyboardButton(text="⬅️ Ta'lim menyusi", callback_data="menu_education")])

    await callback.message.edit_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons_list),
        parse_mode="HTML"
    )
    await callback.answer()


@education_router.callback_query(F.data.startswith("quiz_"), StateFilter("*"))
async def handle_quiz_answer(callback: CallbackQuery):
    """Test javobini tekshirish"""
    parts = callback.data.split("_")
    quiz_idx = int(parts[1])
    user_choice = int(parts[2])

    q = QUIZ_QUESTIONS[quiz_idx]
    is_correct = (user_choice == q["correct"])

    if is_correct:
        alert_text = "🎉 BARAKALLA! To'g'ri javob berdingiz! 👏"
    else:
        correct_option_text = q["options"][q["correct"]]
        alert_text = f"❌ Noto'g'ri! To'g'ri javob: {correct_option_text}"

    await callback.answer(text=alert_text, show_alert=True)

    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➡️ Keyingi test", callback_data="edu_quiz")],
            [InlineKeyboardButton(text="⬅️ Ta'lim menyusi", callback_data="menu_education")]
        ]
    )

    await callback.message.edit_reply_markup(reply_markup=buttons)


@education_router.callback_query(F.data == "edu_fact", StateFilter("*"))
async def handle_edu_fact(callback: CallbackQuery):
    """Qiziqarli fakt ko'rsatish"""
    await increment_user_requests(callback.from_user.id)
    fact = random.choice(FACTS)

    text = (
        f"🧠 <b>Qiziqarli Ilmiy Fakt:</b>\n\n"
        f"{fact}"
    )

    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Boshqa fakt", callback_data="edu_fact")],
            [InlineKeyboardButton(text="⬅️ Ta'lim menyusi", callback_data="menu_education")]
        ]
    )

    await callback.message.edit_text(text=text, reply_markup=buttons, parse_mode="HTML")
    await callback.answer()


@education_router.callback_query(F.data == "edu_top_words", StateFilter("*"))
async def handle_edu_top_words(callback: CallbackQuery):
    """Top foydali so'zlar ro'yxati"""
    await increment_user_requests(callback.from_user.id)

    text = (
        "📚 <b>Kundalik eng kerakli 10 ta ibora:</b>\n\n"
        "1. <b>Never mind</b> — Hechqisi yo'q / Xavotir olmang\n"
        "2. <b>I have no idea</b> — Hech qanday tasavvurim yo'q\n"
        "3. <b>Make yourself at home</b> — O'zingizni uyingizdagidek his qiling\n"
        "4. <b>As soon as possible (ASAP)</b> — Iloji boricha tezroq\n"
        "5. <b>Keep it up</b> — Shunday davom eting\n"
        "6. <b>Take care</b> — O'zingizni ehtiyot qiling\n"
        "7. <b>No way</b> — Bo'lishi mumkin emas\n"
        "8. <b>It's up to you</b> — O'zingiz bilasiz / Qaror sizda\n"
        "9. <b>By the way</b> — Aytgancha\n"
        "10. <b>Good luck</b> — Omad yor bo'lsin!"
    )

    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎯 Test topshirish", callback_data="edu_quiz")],
            [InlineKeyboardButton(text="⬅️ Ta'lim menyusi", callback_data="menu_education")]
        ]
    )

    await callback.message.edit_text(text=text, reply_markup=buttons, parse_mode="HTML")
    await callback.answer()
