from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackContext
from game_info_handler import setup_game_info_handlers  # Подключаем обработчики информации об играх
from registration_handler import setup_registration_handlers  # Подключаем обработчики записи
from manager_handler import setup_manager_handlers, contact_info  # Подключаем обработчики связи с менеджером

# 🔹 Главное меню
async def start(update: Update, context: CallbackContext):
    keyboard = [
        ["🎲 Об Играх", "📝 Записаться"],
        ["📞 Связаться"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

# 🔹 Подключаем обработчики
def setup_handlers(app):
    app.add_handler(CommandHandler("start", start))
    setup_game_info_handlers(app)  # Подключаем обработчики информации об играх
    setup_registration_handlers(app)  # Подключаем обработчики записи
    setup_manager_handlers(app)  # Подключаем обработчики связи с менеджером
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("📞 Связаться"), contact_info))
