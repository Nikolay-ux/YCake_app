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

PM = booking.PlaceManager()

USERNAME, PASSWORD = range(2)

def db_connect():
    return sqlite3.connect('users.db')

def check_user_in_db(username, password):
    conn = db_connect()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM tags WHERE tg_mail = ? AND password = ?', (username, password))
    result = cursor.fetchone()

    conn.close()
    
    return result is not None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите имя пользователя:")
    return USERNAME

async def get_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['username'] = update.message.text
    await update.message.reply_text("Введите пароль:")
    return PASSWORD

async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = context.user_data.get('username')
    password = update.message.text

    if check_user_in_db(username, password):
        # Удаляем предыдущее сообщение
        await update.message.delete()

        keyboard = [
            [InlineKeyboardButton("Забронировать комнату", callback_data="booking")],
            [InlineKeyboardButton("Настройки [WIP]", callback_data="options")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(f"Добро пожаловать, {username}!")
        await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

        return ConversationHandler.END
    else:
        await update.message.reply_text("Неверное имя пользователя или пароль. Попробуйте снова.")
        return ConversationHandler.END
    
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Процесс отменен.')
    return ConversationHandler.END
       
async def handle_back_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton("Забронировать комнату", callback_data="booking")], [InlineKeyboardButton("Настройки [WIP]", callback_data="3")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text("Выберите действие:", reply_markup=reply_markup)
    
async def handle_book_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cities = PM.get_cities()
    keyboard = []
    for city in cities:
        keyboard.append([InlineKeyboardButton(city, callback_data=f'city_{city}')])
    keyboard.append([InlineKeyboardButton("В начало", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)        
    await update.callback_query.edit_message_text("Выберите город:", reply_markup=reply_markup)

async def handle_book_city(update: Update, context: ContextTypes.DEFAULT_TYPE, city) -> None:
    keyboard = []
    rooms = PM.get_rooms(city)
    for i in range(rooms[0].__len__()):
        keyboard.append([InlineKeyboardButton(f'{rooms[0][i]}', callback_data=f'room_{rooms[0][i]}_{rooms[1][i]}')]) 
    keyboard.append([InlineKeyboardButton("В начало", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text("Выберите комнату:", reply_markup=reply_markup)    
    
async def handle_book_room(update: Update, context: ContextTypes.DEFAULT_TYPE, room_id, room_name) -> None:
    dates = []
    current_date = datetime.now()
    for i in range(7):
        dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    keyboard = []
    for date in dates:
        keyboard.append([InlineKeyboardButton(date, callback_data=f'd_room_{room_id}_{date}')])
    keyboard.append([InlineKeyboardButton("В начало", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)        
    await update.callback_query.edit_message_text(f"{room_name} выбрана. Выберите день:", reply_markup=reply_markup)

async def handle_book_time(update: Update, context: ContextTypes.DEFAULT_TYPE, room_id, date) -> None:
    slots = PM.check_spot_availability(room_id, date)
    keyboard = []
    
    for i in range(0, len(slots), 5):
        row = [InlineKeyboardButton(slot, callback_data=f'st_room_{room_id}_{date}_{slot}') for slot in slots[i:i+5]]
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("В начало", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(f"{date}   Выберите время начала:", reply_markup=reply_markup)  
    
async def handle_confirm_booking(update: Update, context: ContextTypes.DEFAULT_TYPE, room_id, date, slot_start) -> None:
    slots = PM.check_spot_availability(room_id, date)
    keyboard = []
    index = slots.index(slot_start)
    slots = slots[index + 1:min(index + 7, len(slots))]
    for i in range(0, len(slots), 3):
        row = [InlineKeyboardButton(slot, callback_data=f'booked_{room_id}_{date}_{slot_start}_{slot}') for slot in slots[i:i+3]]
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("В начало", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text(f"время начала: {slot_start}, выберите время окончания:", reply_markup=reply_markup)  

async def handle_set_booked(update: Update, context: ContextTypes.DEFAULT_TYPE, room_id, date, time_start, time_end) -> None:
    PM.book_spot(room_id, date, time_start, time_end)
    keyboard = [[InlineKeyboardButton("В начало", callback_data="back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(f"Вы успешно забронировали комнату [room name] с {time_start} до {time_end}, {date}!", reply_markup=reply_markup)  
    
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    query = update.callback_query
    await query.answer()

    if query.data == "back":
        await handle_back_button(update, context)

    if query.data == "booking":
        await handle_book_button(update , context)
        
    if query.data.startswith('city_'):
        city = query.data.split('_')[-1]
        await handle_book_city(update, context, city)
        
    if query.data.startswith('room_'):
        room_id = query.data.split('_')[-1]
        room_name = query.data.split('_')[-2]
        await handle_book_room(update, context, room_id, room_name)   
        
    if query.data.startswith('d_room'):
        room_id = int(query.data.split("_")[-2])
        date = query.data.split("_")[-1]
        await handle_book_time(update, context, room_id, date) 
    
    if query.data.startswith('st_room'):
        slot = query.data.split("_")[-1]
        date = query.data.split("_")[-2]
        room_id = int(query.data.split("_")[-3])
        await handle_confirm_booking(update, context, room_id, date, slot)
        
    if query.data.startswith('booked'):
        time_end = query.data.split("_")[-1]
        time_start = query.data.split("_")[-2]
        date = query.data.split("_")[-3]
        room_id = int(query.data.split("_")[-4])
        await handle_set_booked(update, context, room_id, date, time_start, time_end)
        
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

    application.add_handler(CallbackQueryHandler(buttons))

    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()