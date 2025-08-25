import os
import telebot

# Получаем токен из переменной окружения
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Создаём бота
bot = telebot.TeleBot(TOKEN)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я живой бот, работающий на Render.com! 🚀")

# Обработчик любого текста
@bot.message_handler(func=lambda message: True)
def echo(message):
    bot.reply_to(message, f"Вы сказали: {message.text}")

# Запуск бота
if __name__ == '__main__':
    print("Бот запущен...")
    bot.polling(none_stop=True)
