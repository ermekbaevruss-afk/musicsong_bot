import logging
from aiogram import Bot, Dispatcher, executor, types
from googlesearch import search
import os

# 🔑 Токенді жүйеден аламыз (Railway Variables арқылы)
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# 🌐 Тілдер
LANGUAGES = {
    "kk": "Қазақша 🇰🇿",
    "ru": "Русский 🇷🇺",
    "uz": "Oʻzbekcha 🇺🇿"
}

# 🏠 /start
@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    for code, lang in LANGUAGES.items():
        keyboard.add(types.InlineKeyboardButton(text=lang, callback_data=f"lang_{code}"))
    await message.answer(
        "Сәлем! Мен саған кез келген әннің сөзін немесе өзін табуға көмектесем 🎶\n\n"
        "Тілді таңдаңыз 👇",
        reply_markup=keyboard
    )

# 🌍 Тілді таңдау
@dp.callback_query_handler(lambda c: c.data.startswith("lang_"))
async def choose_lang(callback_query: types.CallbackQuery):
    lang = callback_query.data.split("_")[1]
    await callback_query.answer()

    keyboard = types.InlineKeyboardMarkup()
    if lang == "kk":
        keyboard.add(types.InlineKeyboardButton("🎵 Әннің тексі керек", callback_data=f"text_{lang}"))
        keyboard.add(types.InlineKeyboardButton("🎧 Әннің өзі керек", callback_data=f"song_{lang}"))
        await bot.send_message(callback_query.from_user.id, "Таңдаңыз:", reply_markup=keyboard)
    elif lang == "ru":
        keyboard.add(types.InlineKeyboardButton("🎵 Нужен текст песни", callback_data=f"text_{lang}"))
        keyboard.add(types.InlineKeyboardButton("🎧 Нужна сама песня", callback_data=f"song_{lang}"))
        await bot.send_message(callback_query.from_user.id, "Выберите:", reply_markup=keyboard)
    elif lang == "uz":
        keyboard.add(types.InlineKeyboardButton("🎵 Qo‘shiq matni kerak", callback_data=f"text_{lang}"))
        keyboard.add(types.InlineKeyboardButton("🎧 Qo‘shiqning o‘zi kerak", callback_data=f"song_{lang}"))
        await bot.send_message(callback_query.from_user.id, "Tanlang:", reply_markup=keyboard)

# 🎶 Ән мәтіні немесе ән таңдау
@dp.callback_query_handler(lambda c: c.data.startswith("text_") or c.data.startswith("song_"))
async def choose_option(callback_query: types.CallbackQuery):
    choice, lang = callback_query.data.split("_")
    await callback_query.answer()

    if choice == "text":
        if lang == "kk":
            await bot.send_message(callback_query.from_user.id, "Қай әннің мәтіні керек? Автор немесе атауын жазыңыз 🎵")
        elif lang == "ru":
            await bot.send_message(callback_query.from_user.id, "Какой текст песни нужен? Напиши исполнителя или название 🎵")
        elif lang == "uz":
            await bot.send_message(callback_query.from_user.id, "Qaysi qo‘shiq matni kerak? Muallif yoki nomini yozing 🎵")
        await bot.send_message(callback_query.from_user.id, "🔎 Мысал: Rashid Xojasov Ketpe janim")
        dp.register_message_handler(get_lyrics, state=None)
    else:
        if lang == "kk":
            await bot.send_message(callback_query.from_user.id, "Қай ән керек? Автор немесе атауын жазыңыз 🎧")
        elif lang == "ru":
            await bot.send_message(callback_query.from_user.id, "Какую песню ищешь? Напиши исполнителя или название 🎧")
        elif lang == "uz":
            await bot.send_message(callback_query.from_user.id, "Qaysi qo‘shiq kerak? Muallif yoki nomini yozing 🎧")
        await bot.send_message(callback_query.from_user.id, "🔎 Мысал: Jah Khalib Meduza")
        dp.register_message_handler(get_song, state=None)

# 🧾 Ән мәтінін іздеу
async def get_lyrics(message: types.Message):
    query = f"{message.text} lyrics site:genius.com"
    results = list(search(query, num=1))
    if results:
        await message.answer(f"📄 Міне, сол әннің мәтіні:\n{results[0]}")
    else:
        await message.answer("Кешіріңіз, мәтін табылмады 😢")

# 🎧 Ән тыңдау сілтемесін табу
async def get_song(message: types.Message):
    query = f"{message.text} site:youtube.com OR site:open.spotify.com"
    results = list(search(query, num=2))
    if results:
        reply_text = "🎧 Тыңдауға болады:\n\n"
        for link in results:
            reply_text += f"🔗 {link}\n"
        await message.answer(reply_text)
    else:
        await message.answer("Кешіріңіз, ән табылмады 😢")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
