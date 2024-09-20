import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes
from place import PlaceManager
from utils import create_buttons
from datetime import timedelta

# Настройка логгера
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = 'YOUR_BOT_TOKEN'
rooms = 5
manager = PlaceManager(rooms)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Book a room", callback_data="1"), InlineKeyboardButton("Option 2", callback_data="2")],
        [InlineKeyboardButton("Options", callback_data="3")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose:", reply_markup=reply_markup)

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
            keyboard.append([InlineKeyboardButton(f'Room {i+1}', callback_data=f'room_{i+1}')])        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Choose a room:", reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Use /start to test this bot.")

def main() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(buttons))
    application.add_handler(CommandHandler("help", help_command))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
