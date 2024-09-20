from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def create_buttons(buttons_data):
    keyboard = []
    for button_data in buttons_data:
        button = InlineKeyboardButton(button_data['text'], callback_data=button_data['callback_data'])
        keyboard.append([button])
    return InlineKeyboardMarkup(keyboard)
