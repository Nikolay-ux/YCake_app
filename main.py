import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    CallbackQueryHandler, 
    ContextTypes
)
from dotenv import load_dotenv
import os

# Загружаем переменные окружения из .env файла
load_dotenv()

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Функция для команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Создаем две кнопки
    keyboard = [
        [
            InlineKeyboardButton("Кнопка 1", callback_data='1'),
            InlineKeyboardButton("Кнопка 2", callback_data='2')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправляем сообщение с кнопками
    await update.message.reply_text('Выберите одну из кнопок:', reply_markup=reply_markup)

# Обработка нажатия на кнопки
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Выводим сообщение о выбранной кнопке
    await query.edit_message_text(text=f"Вы выбрали: {query.data}")

if __name__ == '__main__':
    # Создаем приложение с токеном из переменных окружения
    application = ApplicationBuilder().token(os.getenv('TOKEN')).build()

    # Обработчик для команды /start
    application.add_handler(CommandHandler('start', start))
    
    # Обработчик для нажатий на кнопки
    application.add_handler(CallbackQueryHandler(button))

    # Запуск бота
    application.run_polling()
