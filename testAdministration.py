from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Ваш API-токен от BotFather
f = open('token.txt', "r")
TOKEN = f.read().strip()
f.close()

# ID пользователя, которому разрешено использовать бота (например, ID администратора)
ALLOWED_USER_ID = 123456789  # Замените на реальный ID

# Функция для проверки прав доступа
# def check_user(update: Update):
#     user_id = update.message.from_user.id
#     if user_id == ALLOWED_USER_ID:
#         return True
#     else:
#         update.message.reply_text("У вас нет прав для использования этого бота.")
#         return False

# Функция для получения и отправки ID пользователя
async def get_user_id(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    # Выводим ID пользователя в консоль
    print(f"ID пользователя: {user_id}")
    # Отправляем ID пользователя обратно ему в чат
    await update.message.reply_text(f"Ваш ID: {user_id}")

# Функция для обработки команды /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Привет! Я ваш бот. Отправьте мне сообщение, и я его повторю.")

# Функция для обработки любых текстовых сообщений
async def echo(update: Update, context: CallbackContext):
    # Отправляем обратно тот же текст, который прислал пользователь
    await update.message.reply_text(update.message.text)
    # Отправляем ID пользователя в ответ
    await get_user_id(update, context)

# Главная функция, которая запускает бота
def main():
    # Создаем объект Application и передаем ему токен бота
    application = Application.builder().token(TOKEN).build()

    # Обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # Обработчик всех текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND))

    # Запуск бота с опросом
    application.run_polling()

    print("Бот запущен. Нажмите Ctrl+C для завершения.")

if __name__ == "__main__":
    main()
