from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import MessageHandler, filters, CallbackContext, ConversationHandler
from google_sheets import add_game_record  # Функция записи в таблицу

# Этапы диалога
GAME_SELECTION, CHILD_NAME, PARENT_NAME, PHONE, CHILD_AGE = range(5)

# 🔹 Главное меню
MAIN_MENU = ReplyKeyboardMarkup(
    [["🎲 Об Играх", "📝 Записаться"], ["📞 Связаться"]],
    resize_keyboard=True
)

# 🔹 Список игр
GAMES = [
    "📝 Запись 🐉 Стражи Огня. Туманный Альбион",
    "📝 Запись 🚀 Звездные Войны. Пробуждение Ситхов",
    "📝 Запись ⚔️ КРД. Рассеченная Судьба",
    "📝 Запись 🌲 ДнД. Непройденные тропы",
    "📝 Запись 🧙 Гарри Поттер. Хранители Мира",
    "📝 Запись 🩸 Стражи Огня. Война Шипов",
    "📝 Запись 🏰 Средиземье. Цитадель Света"
]

# 🔹 Главное меню регистрации
async def start_registration(update: Update, context: CallbackContext):
    keyboard = [[game] for game in GAMES] + [["🏠 В главное меню"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text("Выберите игру, на которую хотите записаться:", reply_markup=reply_markup)
    return GAME_SELECTION

# 🔹 Выбор игры
async def game_selected(update: Update, context: CallbackContext):
    game_name = update.message.text.replace("📝 Запись ", "")

    if game_name not in [g.replace("📝 Запись ", "") for g in GAMES]:
        await update.message.reply_text("❌ Такой игры нет в списке. Выберите из предложенного.")
        return GAME_SELECTION

    context.user_data["game_name"] = game_name

    # Показываем кнопку "🏠 В главное меню"
    reply_markup = ReplyKeyboardMarkup([["🏠 В главное меню"]], resize_keyboard=True)
    await update.message.reply_text("Введите имя ребенка:", reply_markup=reply_markup)
    return CHILD_NAME

# 🔹 Ввод имени ребенка
async def child_name(update: Update, context: CallbackContext):
    if update.message.text == "🏠 В главное меню":
        return await cancel_registration(update, context)

    context.user_data["child_name"] = update.message.text
    reply_markup = ReplyKeyboardMarkup([["🏠 В главное меню"]], resize_keyboard=True)
    await update.message.reply_text("Введите имя родителя:", reply_markup=reply_markup)
    return PARENT_NAME

# 🔹 Ввод имени родителя
async def parent_name(update: Update, context: CallbackContext):
    if update.message.text == "🏠 В главное меню":
        return await cancel_registration(update, context)

    context.user_data["parent_name"] = update.message.text
    reply_markup = ReplyKeyboardMarkup([["🏠 В главное меню"]], resize_keyboard=True)
    await update.message.reply_text("Введите контактный номер телефона:", reply_markup=reply_markup)
    return PHONE

# 🔹 Ввод телефона
async def phone(update: Update, context: CallbackContext):
    if update.message.text == "🏠 В главное меню":
        return await cancel_registration(update, context)

    context.user_data["phone"] = update.message.text
    reply_markup = ReplyKeyboardMarkup([["🏠 В главное меню"]], resize_keyboard=True)
    await update.message.reply_text("Сколько лет ребенку?", reply_markup=reply_markup)
    return CHILD_AGE

# 🔹 Ввод возраста ребенка
async def child_age(update: Update, context: CallbackContext):
    if update.message.text == "🏠 В главное меню":
        return await cancel_registration(update, context)

    context.user_data["child_age"] = update.message.text

    # Записываем в Google Таблицу
    add_game_record(
        user_id=update.message.from_user.id,
        username=update.message.from_user.username or update.message.from_user.first_name,
        game_name=context.user_data["game_name"],
        child_name=context.user_data["child_name"],
        parent_name=context.user_data["parent_name"],
        phone=context.user_data["phone"],
        child_age=context.user_data["child_age"]
    )

    # Меню исчезает после завершения записи
    await update.message.reply_text(
        "✅ Спасибо! Ваша заявка принята. Менеджер скоро свяжется с вами.", 
        reply_markup=MAIN_MENU
    )
    return ConversationHandler.END

# 🔹 Отмена регистрации и возврат в главное меню
async def cancel_registration(update: Update, context: CallbackContext):
    """Завершает регистрацию и возвращает в главное меню"""
    context.user_data.clear()  # Очистка данных пользователя
    await update.message.reply_text("🚫 Регистрация отменена. Вы вернулись в главное меню.", reply_markup=MAIN_MENU)
    return ConversationHandler.END

# Подключаем обработчики
def setup_registration_handlers(app):
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & filters.Regex("^📝 Записаться$"), start_registration)],
        states={
            GAME_SELECTION: [
                MessageHandler(filters.TEXT & filters.Regex("^📝 Запись "), game_selected),
                MessageHandler(filters.TEXT & filters.Regex("^🏠 В главное меню$"), cancel_registration)
            ],
            CHILD_NAME: [
                MessageHandler(filters.TEXT, child_name)
            ],
            PARENT_NAME: [
                MessageHandler(filters.TEXT, parent_name)
            ],
            PHONE: [
                MessageHandler(filters.TEXT, phone)
            ],
            CHILD_AGE: [
                MessageHandler(filters.TEXT, child_age)
            ],
        },
        fallbacks=[MessageHandler(filters.TEXT & filters.Regex("^🏠 В главное меню$"), cancel_registration)]
    )
    app.add_handler(conv_handler)
