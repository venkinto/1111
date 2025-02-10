from telegram.ext import Application
from config import API_TOKEN
from handlers import setup_handlers  # Основные обработчики
from manager_handler import setup_manager_handlers  # Чат с менеджером
from game_info_handler import setup_game_info_handlers  # Информация об играх
from registration_handler import setup_registration_handlers  # Регистрация

def main():
    app = Application.builder().token(API_TOKEN).build()
    setup_handlers(app)  # Основные обработчики
    setup_game_info_handlers(app)  # Информация об играх
    setup_registration_handlers(app)  # Регистрация
    setup_manager_handlers(app)  # Чат с менеджером

    print("Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
