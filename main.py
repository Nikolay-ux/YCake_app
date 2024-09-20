f = open('token.txt', "r")
TOKEN = f.read().strip()
f.close()
    
import logging
import booking
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

rooms = 5
PlaceManager = booking.PlaceManager(rooms)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Book a room", callback_data="1"), InlineKeyboardButton("Option 2", callback_data="2")],
        [InlineKeyboardButton("Options", callback_data="3")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose:", reply_markup=reply_markup)

# async def private_meeting_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
   
   
def create_buttons(buttons_data):
    keyboard = []
    for button_data in buttons_data:
        button = InlineKeyboardButton(button_data['text'], callback_data=button_data['callback_data'])
        keyboard.append([button])
    return InlineKeyboardMarkup(keyboard)   

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    await query.answer()

    if query.data == "1":
        keyboard = [
        [InlineKeyboardButton("Private meeting", callback_data="private")],
        [InlineKeyboardButton("Public event", callback_data="public")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)        
        await query.edit_message_text("Please choose:", reply_markup=reply_markup)
        
    if query.data == "private":
        keyboard = []
        for i in range(rooms):
            keyboard.append([InlineKeyboardButton(f'Room {i+1}', callback_data=f'private_room_{i+1}')])        
        reply_markup = InlineKeyboardMarkup(keyboard)        
        await query.edit_message_text("Choose a room:", reply_markup=reply_markup)
    if query.data.startswith("private_room_"):
        room_id = int(query.data.split("_")[-1])
        
        reply_markup = InlineKeyboardMarkup(keyboard)        
        await query.edit_message_text(f"Room {room_id} selected. Please choose a time and duration:", reply_markup=reply_markup)
    # if query.data    

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Use /start to test this bot.")


def main() -> None:
    
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(buttons))
    # application.add_handler(CallbackQueryHandler(private_meeting_creation))
    application.add_handler(CommandHandler("help", help_command))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()