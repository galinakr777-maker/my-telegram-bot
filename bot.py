import os
import telebot
import pandas as pd
from flask import Flask
import threading

# === НАСТРОЙКИ ===
TOKEN = os.getenv("TELEGRAM_TOKEN")
EXCEL_FILE = "оплаты 2025.xlsx"

# Создаём бота
bot = telebot.TeleBot(TOKEN)

# Загружаем данные
def load_data():
    try:
        df = pd.read_excel(EXCEL_FILE)
        df["Номер участка"] = pd.to_numeric(df["Номер участка"], errors='coerce')
        return df.dropna(subset=["Номер участка"])
    except Exception as e:
        print(f"Ошибка загрузки Excel: {e}")
        return pd.DataFrame()

data = load_data()

# === Веб-сервер для Render ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Бот работает! Это техническая страница для Render.", 200

@app.route('/health')
def health():
    return "OK", 200

# Запуск веб-сервера в отдельном потоке
def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# === ОБРАБОТЧИКИ БОТА ===
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "Привет! Введите номер участка, и я покажу данные."
    )

@bot.message_handler(func=lambda message: True)
def find_plot(message):
    if not data.empty:
        try:
            plot_number = int(message.text.strip())
            result = data[data["Номер участка"] == plot_number]

            if not result.empty:
                # Формируем ответ из всех колонок
                row = result.iloc[0]  # Берём найденную строку
                response = "Данные по участку:\n\n"
                for col, val in row.items():
                    if pd.notna(val):  # Проверяем, что значение не пустое
                        response += f"*{col}:* {val}\n"
                bot.reply_to(message, response, parse_mode="Markdown")
            else:
                bot.reply_to(message, f"Участок с номером {plot_number} не найден.")
        except ValueError:
            bot.reply_to(message, "Введите **целое число** — номер участка.")
        except Exception as e:
            bot.reply_to(message, f"Произошла ошибка: {e}")
    else:
        bot.reply_to(message, "❌ Не удалось загрузить данные.")

# === Запуск ===
if __name__ == '__main__':
    # Запускаем веб-сервер в фоне
    web_thread = threading.Thread(target=run_web)
    web_thread.daemon = True
    web_thread.start()

    # Запускаем бота
    print("Запуск Telegram-бота...")
    bot.polling(none_stop=True)
