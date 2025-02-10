from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler, MessageHandler, filters, CommandHandler

from config import ADMIN_ID  # ID менеджера (админа)

# 🔹 Активные чаты (связываем пользователя и менеджера)
active_chats = {}

# 🔹 Главное меню
MAIN_MENU = ReplyKeyboardMarkup(
    [["🎲 Об Играх", "📝 Записаться"], ["📞 Связаться"]],
    resize_keyboard=True
)

# 🔹 Пользователь нажимает "📞 Связаться"
async def contact_info(update: Update, context: CallbackContext):
    keyboard = [[InlineKeyboardButton("📢 Позвать менеджера", callback_data="call_manager")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "📞 Вы можете позвонить нам по номеру: +7 916 906-96-65\n"
        "Или позвать менеджера в чат.",
        reply_markup=reply_markup
    )

# 🔹 Пользователь вызывает менеджера
async def call_manager(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username or query.from_user.first_name

    # Если уже есть активный чат, уведомляем пользователя
    if user_id in active_chats:
        await query.answer("Вы уже в чате с менеджером.")
        return
    
    # Добавляем пользователя в активные чаты
    active_chats[user_id] = ADMIN_ID  # Связываем с менеджером

    # Отправляем сообщение менеджеру с кнопкой "Начать чат"
    keyboard = [[InlineKeyboardButton("📝 Начать чат", callback_data=f"start_chat_{user_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📢 Запрос на чат от @{username} (ID: {user_id}).",
        reply_markup=reply_markup
    )

    # Подтверждение пользователю
    await query.answer("Менеджер будет уведомлён!")
    await query.edit_message_text("✅ Менеджер уже в курсе, скоро свяжется с вами!")

# 🔹 Менеджер принимает чат
async def start_chat(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = int(query.data.split("_")[2])  # Берём ID пользователя

    if user_id not in active_chats:
        await query.answer("Этот чат уже закрыт.")
        return

    active_chats[user_id] = ADMIN_ID  # Связываем с менеджером

    # Кнопка "❌ Окончить чат" для менеджера
    end_chat_button = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Окончить чат", callback_data="end_chat")]])

    await context.bot.send_message(chat_id=user_id, text="💬 Менеджер подключился. Вы можете начать общение.")
    await context.bot.send_message(chat_id=ADMIN_ID, text=f"💬 Вы начали чат с пользователем {user_id}.", reply_markup=end_chat_button)

    await query.answer()

# 🔹 Пересылка сообщений между пользователем и менеджером
async def chat_forward(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    # Если пишет пользователь — пересылаем менеджеру
    if user_id in active_chats and active_chats[user_id] == ADMIN_ID:
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"👤 @{update.message.from_user.username}: {update.message.text}")
    
    # Если пишет менеджер — пересылаем пользователю
    elif user_id == ADMIN_ID:
        for user in active_chats:
            if active_chats[user] == ADMIN_ID:
                await context.bot.send_message(chat_id=user, text=f"📩 Менеджер: {update.message.text}")

# 🔹 Завершение чата (кнопка и команда)
async def end_chat(update: Update, context: CallbackContext):
    query = update.callback_query if update.callback_query else None
    user_id = query.from_user.id if query else update.message.from_user.id

    # Если менеджер завершает чат
    if user_id == ADMIN_ID:
        for user in list(active_chats.keys()):
            if active_chats[user] == ADMIN_ID:
                await context.bot.send_message(chat_id=user, text="🚫 Чат завершён менеджером.", reply_markup=MAIN_MENU)
                del active_chats[user]
    
    # Если пользователь завершает чат
    elif user_id in active_chats:
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"❌ Пользователь {user_id} завершил чат.")
        del active_chats[user_id]

    if query:
        await query.answer("Чат завершён.")
        await query.message.delete()  # Удаляем кнопку "❌ Окончить чат" у менеджера
    else:
        await update.message.reply_text("✅ Чат завершён.", reply_markup=MAIN_MENU)

# 🔹 Подключаем обработчики
def setup_manager_handlers(app):
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex("📞 Связаться"), contact_info))  # Кнопка "Связаться"
    app.add_handler(CallbackQueryHandler(call_manager, pattern="call_manager"))  # Кнопка "Позвать менеджера"
    app.add_handler(CallbackQueryHandler(start_chat, pattern="start_chat_"))  # Менеджер принимает чат
    app.add_handler(CallbackQueryHandler(end_chat, pattern="end_chat"))  # Менеджер завершает чат кнопкой
    app.add_handler(MessageHandler(filters.TEXT, chat_forward))  # Пересылка сообщений
    app.add_handler(CommandHandler("endchat", end_chat))  # Завершение чата через команду
