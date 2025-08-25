import os
import telebot
import pandas as pd

# === НАСТРОЙКИ ===
TOKEN = os.getenv("TELEGRAM_TOKEN")
EXCEL_FILE = "оплаты 2025.xlsx"  # Имя вашего Excel-файла

# Создаём бота
bot = telebot.TeleBot(TOKEN)

# Загружаем таблицу при запуске
def load_data():
    try:
        df = pd.read_excel(EXCEL_FILE)
        # Приводим номер участка к числу, если он был текстом
        df["Номер участка"] = pd.to_numeric(df["Номер участка"], errors='coerce')
        return df.dropna(subset=["Номер участка"])  # Убираем строки без номера
    except Exception as e:
        print(f"Ошибка при загрузке Excel: {e}")
        return pd.DataFrame()

# Храним таблицу в памяти
data = load_data()

# === ОБРАБОТЧИКИ БОТА ===

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "Привет! Я — бот для поиска информации по участкам.\n"
        "Введите номер участка (только число), и я покажу данные."
    )

@bot.message_handler(func=lambda message: True)
def find_plot(message):
    if not data.empty:
        try:
            # Пытаемся преобразовать ввод в число
            plot_number = int(message.text.strip())

            # Ищем строку по номеру участка
            result = data[data["Номер участка"] == plot_number]

            if not result.empty:
                # Формируем ответ из всех колонок
                row = result.iloc[0]  # Берём первую (и единственную) найденную строку
                response = "Данные по участку:\n\n"
                for col, val in row.items():
                    if pd.notna(val):  # Проверяем, что значение не пустое
                        response += f"*{col}:* {val}\n"
                bot.reply_to(message, response, parse_mode="Markdown")
            else:
                bot.reply_to(message, f"Участок с номером {plot_number} не найден.")
        except ValueError:
            bot.reply_to(message, "Пожалуйста, введите **целое число** — номер участка.")
        except Exception as e:
            bot.reply_to(message, f"Произошла ошибка: {e}")
    else:
        bot.reply_to(message, "❌ Не удалось загрузить данные. Обратитесь к администратору.")

# Запуск бота
if __name__ == '__main__':
    if data.empty:
        print("⚠️ Предупреждение: данные не загружены. Проверьте файл Excel.")
    else:
        print(f"✅ Загружено {len(data)} строк из Excel.")
    bot.polling(none_stop=True)   
