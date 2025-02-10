from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import MessageHandler, filters, CallbackContext
from config import CHANNEL_ID

# 🔹 ID сообщений с анонсами игр (замени на реальные ID из канала)
GAME_ANNOUNCEMENTS = {
    "ℹ️ Инфо: 🐉 Стражи Огня. Туманный Альбион": 8,  # ID сообщения в Telegram
    "ℹ️ Инфо: 🚀 Звездные Войны. Пробуждение Ситхов": 7,
    "ℹ️ Инфо: ⚔️ КРД. Рассеченная Судьба": 6,
    "ℹ️ Инфо: 🌲 ДнД. Непройденные тропы": 5,
    "ℹ️ Инфо: 🧙 Гарри Поттер. Хранители Мира": 4,
    "ℹ️ Инфо: 🩸 Стражи Огня. Война Шипов": 3,
    "ℹ️ Инфо: 🏰 Средиземье. Цитадель Света": 2,
}

# 🔹 Меню с описанием игр
async def about_games(update: Update, context: CallbackContext):
    keyboard = [
        ["ℹ️ Инфо: 🐉 Стражи Огня. Туманный Альбион", "ℹ️ Инфо: 🚀 Звездные Войны. Пробуждение Ситхов"],
        ["ℹ️ Инфо: ⚔️ КРД. Рассеченная Судьба", "ℹ️ Инфо: 🌲 ДнД. Непройденные тропы"],
        ["ℹ️ Инфо: 🧙 Гарри Поттер. Хранители Мира", "ℹ️ Инфо: 🩸 Стражи Огня. Война Шипов"],
        ["ℹ️ Инфо: 🏰 Средиземье. Цитадель Света", "🔙 Назад"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите игру, чтобы узнать о ней подробнее:", reply_markup=reply_markup)

# 🔹 Отправляем анонс игры (пересылаем сообщение)
async def game_details(update: Update, context: CallbackContext):
    game_name = update.message.text.strip()
    message_id = GAME_ANNOUNCEMENTS.get(game_name)

    if message_id:
        await context.bot.forward_message(chat_id=update.message.chat_id, from_chat_id=CHANNEL_ID, message_id=message_id)
    else:
        await update.message.reply_text("❌ Анонс этой игры не найден.")

# 🔹 Обработчик кнопки "🔙 Назад"
async def back_to_main(update: Update, context: CallbackContext):
    from handlers import start
    await start(update, context)

# 🔹 Подключаем обработчики
def setup_game_info_handlers(app):
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^🎲 Об Играх$"), about_games))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^ℹ️ Инфо: .*"), game_details))
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^🔙 Назад$"), back_to_main))
