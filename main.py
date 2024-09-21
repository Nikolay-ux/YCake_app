f = open('token.txt', "r")
TOKEN = f.read().strip()
f.close()
    
import logging
import booking
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes
from datetime import datetime, timedelta

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

areas = 3
PM = booking.PlaceManager()

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

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(buttons))
    application.add_handler(CommandHandler("help", help_command))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()