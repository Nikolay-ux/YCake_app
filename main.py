import logging
import os
import sqlite3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes, 
    ConversationHandler
)
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Определение этапов в разговоре
USERNAME, PASSWORD = range(2)

# Подключение к базе данных SQLite
def db_connect():
    return sqlite3.connect('people.db')

# Функция для проверки пользователя и пароля
def check_user_in_db(username, password):
    conn = db_connect()
    cursor = conn.cursor()

    # SQL запрос для проверки логина и пароля
    #query = "SELECT tg_mail AND password FROM tags WHERE tg_mail = ? AND password = ?"
    cursor.execute('SELECT tg_mail AND password FROM tags WHERE tg_mail = ? AND password = ?', (username, password))
    result = cursor.fetchone()

    conn.close()
    
    return result is not None

# Функция для команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите имя пользователя:")
    return USERNAME

# Получение имени пользователя
async def get_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['username'] = update.message.text
    await update.message.reply_text("Введите пароль:")
    return PASSWORD

# Получение пароля и проверка через базу данных
async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = context.user_data.get('username')
    password = update.message.text

    # Проверка логина и пароля через базу данных
    if check_user_in_db(username, password):
        # Удаляем предыдущее сообщение
        await update.message.delete()

        # Создаем клавиатуру с кнопками
        keyboard = [
            [InlineKeyboardButton("Book a room", callback_data="booking")],
            [InlineKeyboardButton("Options", callback_data="options")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Отправляем приветствие и клавиатуру
        await update.message.reply_text(f"Добро пожаловать, {username}!")
        await update.message.reply_text("Please choose:", reply_markup=reply_markup)

        return ConversationHandler.END
    else:
        await update.message.reply_text("Неверное имя пользователя или пароль. Попробуйте снова.")
        return ConversationHandler.END

# Обработчик отмены
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Процесс отменен.')
    return ConversationHandler.END

if __name__ == '__main__':
    # Создаем приложение с токеном из переменных окружения
    application = ApplicationBuilder().token(os.getenv('TOKEN')).build()

    # Создаем ConversationHandler для взаимодействия с пользователем
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_username)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Добавляем ConversationHandler для обработки ввода имени и пароля
    application.add_handler(conv_handler)

    # Запуск бота
    application.run_polling()
