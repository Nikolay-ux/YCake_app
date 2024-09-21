f = open('token.txt', "r")
TOKEN = f.read().strip()
f.close()
    
import logging
import booking
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes
from datetime import datetime, timedelta

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

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

areas = 3
PlaceManager = booking.PlaceManager()

USERNAME, PASSWORD = range(2)

# Подключение к базе данных SQLite
def db_connect():
    return sqlite3.connect('users.db')

# Функция для проверки пользователя и пароля
def check_user_in_db(username, password):
    conn = db_connect()
    cursor = conn.cursor()

    # SQL запрос для проверки логина и пароля
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
    
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Процесс отменен.')
    return ConversationHandler.END
       

async def handle_back_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton("Book a room", callback_data="booking")], [InlineKeyboardButton("Options", callback_data="3")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text("Please choose:", reply_markup=reply_markup)
    
async def handle_book_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cities = PM.get_cities()
    keyboard = []
    for city in cities:
        keyboard.append([InlineKeyboardButton(city, callback_data=f'city_{city}')])
    keyboard.append([InlineKeyboardButton("Back", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)        
    await update.callback_query.edit_message_text("Please choose:", reply_markup=reply_markup)

async def handle_book_city(update: Update, context: ContextTypes.DEFAULT_TYPE, city) -> None:
    keyboard = []
    rooms = PM.get_rooms(city)
    for i in range(rooms[0].__len__()):
        keyboard.append([InlineKeyboardButton(f'{rooms[0][i]}', callback_data=f'room_{rooms[0][i]}_{rooms[1][i]}')]) 
    keyboard.append([InlineKeyboardButton("Back", callback_data="back")])  
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text("Choose a room:", reply_markup=reply_markup)    
    
async def handle_book_room(update: Update, context: ContextTypes.DEFAULT_TYPE, room_id, room_name) -> None:
    dates = []
    current_date = datetime.now()
    for i in range(7):
        dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    keyboard = []
    for date in dates:
        keyboard.append([InlineKeyboardButton(date, callback_data=f'ddroom_{room_id}_{date}')])
    keyboard.append([InlineKeyboardButton("Back", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)        
    await update.callback_query.edit_message_text(f"{room_name} selected. Please choose a day:", reply_markup=reply_markup)

async def handle_book_time(update: Update, context: ContextTypes.DEFAULT_TYPE, room_id, date) -> None:
    slots = PM.check_spot_availability(room_id, date)
    keyboard = []
    
    for i in range(0, len(slots), 5):
        row = [InlineKeyboardButton(slot, callback_data=f'private_room_{room_id}_{date}_{slot}') for slot in slots[i:i+5]]
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("Back", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(f"{date} selected. Please choose a day:", reply_markup=reply_markup)       
    

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    await query.answer()

    if query.data == "back":
        await handle_back_button(update, context)

    if query.data == "booking":
        await handle_book_button(update , context)
        
    if query.data.startswith('city_'):
        city = query.data.split('_')[-1]
        await handle_book_city(update, context, city)
        
    if query.data.startswith('ddroom_'):
        room_id = int(query.data.split("_")[-2])
        date = query.data.split("_")[-1]
        await handle_book_time(update, context, room_id, date) 
        
    elif query.data.startswith('room_'):
        room_id = query.data.split('_')[-1]
        room_name = query.data.split('_')[-2]
        await handle_book_room(update, context, room_id, room_name)
 
        
    # query.data.startswith("private_room_%d_"):
   

    # if query.data    

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Use /start to test this bot.")


def main() -> None:
    
    application = Application.builder().token(TOKEN).build()

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

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()