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

rooms = 5
areas = 3
PlaceManager = booking.PlaceManager(rooms)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Book a room", callback_data="booking")],
        [InlineKeyboardButton("Options", callback_data="3")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose:", reply_markup=reply_markup)

# async def private_meeting_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
   

async def handle_back_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton("Book a room", callback_data="booking")], [InlineKeyboardButton("Options", callback_data="3")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text("Please choose:", reply_markup=reply_markup)
    
async def handle_book_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [[InlineKeyboardButton("Private meeting", callback_data="private")],[InlineKeyboardButton("Public event", callback_data="public")]]
    keyboard.append([InlineKeyboardButton("Back", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)        
    await update.callback_query.edit_message_text("Please choose:", reply_markup=reply_markup)

async def handle_private_booking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = []
    for i in range(rooms):
        keyboard.append([InlineKeyboardButton(f'Room {i+1}', callback_data=f'private_room_{i+1}')]) 
    keyboard.append([InlineKeyboardButton("Back", callback_data="back")])  
    reply_markup = InlineKeyboardMarkup(keyboard)        
    await update.callback_query.edit_message_text("Choose a room:", reply_markup=reply_markup)    
    
async def handle_public_booking(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = []
    for i in range(areas):
        keyboard.append([InlineKeyboardButton(f'Area {i+1}', callback_data=f'public_area_{i+1}')]) 
    keyboard.append([InlineKeyboardButton("Back", callback_data="back")])   
    reply_markup = InlineKeyboardMarkup(keyboard)        
    await update.callback_query.edit_message_text("Choose an Area:", reply_markup=reply_markup)
    
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
        
    await update.callback_query.edit_message_text(f"Room {room_id} selected. Please choose a day:", reply_markup=reply_markup)

async def handle_public_booking_room(update: Update, context: ContextTypes.DEFAULT_TYPE, area_id) -> None:
    dates = []
    current_date = datetime.now()
    for i in range(7):
        dates.append(current_date.strftime("%d.%m"))
        current_date += timedelta(days=1)
        
    keyboard = []
    for date in dates:
        keyboard.append([InlineKeyboardButton(date, callback_data=f'public_area_{area_id}_{date}')])
    keyboard.append([InlineKeyboardButton("Back", callback_data="back")])
    reply_markup = InlineKeyboardMarkup(keyboard)        
    
    reply_markup = InlineKeyboardMarkup(keyboard)     
    await update.callback_query.edit_message_text(f"Area {area_id} selected. Please choose a day:", reply_markup=reply_markup)    

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    await query.answer()

    if query.data == "back":
        await handle_back_button(update, context)

    if query.data == "booking":
        await handle_book_button(update , context)
        
    if query.data == "private":
        await handle_private_booking(update, context)
 
    if query.data == "public":
        await handle_public_booking(update, context)
       
    if query.data.startswith("private_room_"):
        room_id = int(query.data.split("_")[-1])        
        await handle_private_booking_room(update, context, room_id)
            
    if query.data.startswith("public_area_"):
        area_id = int(query.data.split("_")[-1])        
        await handle_public_booking_room(update, context, area_id)
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