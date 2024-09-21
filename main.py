from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes
from datetime import datetime, timedelta
from room_booking import RoomBooking  # Импортируем наш класс для работы с базой данных

# Чтение токена бота
f = open('token.txt', "r")
TOKEN = f.read().strip()
f.close()

# Логирование
import logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Подключение к базе данных
db_path = 'room_booking.db'
room_booking = RoomBooking(db_path)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Book a room", callback_data="booking")],
        [InlineKeyboardButton("Options", callback_data="3")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose:", reply_markup=reply_markup)

async def handle_back_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton("Book a room", callback_data="booking")], [InlineKeyboardButton("Options", callback_data="3")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text("Please choose:", reply_markup=reply_markup)

async def handle_book_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton("Private meeting", callback_data="private")],
                [InlineKeyboardButton("Public event", callback_data="public")]]
    keyboard.append([InlineKeyboardButton("Back", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text("Please choose:", reply_markup=reply_markup)

async def handle_private_booking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = []
    
    # Получаем список всех комнат из базы данных
    with room_booking.conn:
        rooms = room_booking.conn.execute("SELECT id, room_name FROM rooms").fetchall()
    
    # Создаем кнопки для каждой комнаты
    for room_id, room_name in rooms:
        keyboard.append([InlineKeyboardButton(f'{room_name}', callback_data=f'private_room_{room_id}')])
    
    keyboard.append([InlineKeyboardButton("Back", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.edit_message_text("Choose a room:", reply_markup=reply_markup)

async def handle_private_booking_room(update: Update, context: ContextTypes.DEFAULT_TYPE, room_id) -> None:
    dates = []
    current_date = datetime.now()
    for i in range(7):
        dates.append(current_date.strftime("%d.%m"))
        current_date += timedelta(days=1)
    
    keyboard = []
    for date in dates:
        keyboard.append([InlineKeyboardButton(date, callback_data=f'private_room_{room_id}_{date}')])
    
    keyboard.append([InlineKeyboardButton("Back", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Получаем название комнаты из базы данных для вывода в сообщении
    with room_booking.conn:
        room_name = room_booking.conn.execute("SELECT room_name FROM rooms WHERE id = ?", (room_id,)).fetchone()[0]
    
    await update.callback_query.edit_message_text(f"{room_name} selected. Please choose a day:", reply_markup=reply_markup)

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "back":
        await handle_back_button(update, context)

    if query.data == "booking":
        await handle_book_button(update , context)
        
    if query.data == "private":
        await handle_private_booking(update, context)
       
    if query.data.startswith("private_room_"):
        room_id = int(query.data.split("_")[-1])
        await handle_private_booking_room(update, context, room_id)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Use /start to test this bot.")

def main() -> None:
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(buttons))
    application.add_handler(CommandHandler("help", help_command))

    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    finally:
        room_booking.close()

if __name__ == "__main__":
    main()
