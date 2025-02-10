import gspread
from oauth2client.service_account import ServiceAccountCredentials
from config import CREDENTIALS_FILE

# ✅ Название таблицы и листа (замени на свои)
SHEET_NAME = "Записи на игры"  # Название таблицы в Google Sheets
WORKSHEET_NAME = "Лист1"  # Название листа (по умолчанию "Лист1", если не меняли)

# ✅ Путь к файлу с ключами (убедись, что `credentials.json` лежит в папке с ботом)

# 🔹 Подключение к Google API
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]

creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)

# 🔹 Открываем таблицу и лист
try:
    sheet = client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)
    print(f"✅ Успешное подключение к таблице: {SHEET_NAME} ({WORKSHEET_NAME})")
except gspread.exceptions.SpreadsheetNotFound:
    print(f"❌ Ошибка: Таблица '{SHEET_NAME}' не найдена! Проверь название.")
    exit()
except gspread.exceptions.WorksheetNotFound:
    print(f"❌ Ошибка: Лист '{WORKSHEET_NAME}' не найден в таблице!")
    exit()

# 🔹 Функция записи данных в таблицу
def add_game_record(user_id, username, game_name, child_name, parent_name, phone, child_age):
    try:
        sheet.append_row([str(user_id), username, game_name, child_name, parent_name, phone, str(child_age)])
        print(f"✅ Данные записаны: {username} ({user_id}) -> {game_name}")
    except Exception as e:
        print(f"❌ Ошибка записи в Google Sheets: {e}")
