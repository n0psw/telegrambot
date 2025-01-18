from flask import Flask
import threading
import os

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
from telegram.ext.filters import TEXT

# Создаем Flask сервер
app = Flask(__name__)

@app.route("/")
def home():
    return "Бот работает!"

# Получаем токен и Chat ID из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

applications = []

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        "Добро пожаловать в Master Sat Tech Support! Напишите вашу проблему, и мы рассмотрим вашу заявку."
    )

def submit_application(update: Update, context: CallbackContext) -> None:
    global applications
    user = update.message.from_user
    text = update.message.text

    applications.append({"user_id": user.id, "username": user.username, "text": text})
    update.message.reply_text("Спасибо за вашу заявку! Мы свяжемся с вами в ближайшее время.")

    if ADMIN_CHAT_ID:
        context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"Новая заявка:\n\nОт: @{user.username} (ID: {user.id})\nТекст: {text}"
        )

def view_applications(update: Update, context: CallbackContext) -> None:
    if str(update.message.chat_id) == ADMIN_CHAT_ID:
        if applications:
            response = "Список заявок:\n"
            for i, app in enumerate(applications, start=1):
                response += f"{i}. @{app['username']} (ID: {app['user_id']}): {app['text']}\n"
            update.message.reply_text(response)
        else:
            update.message.reply_text("Заявок пока нет.")
    else:
        update.message.reply_text("Эта команда доступна только администратору.")

def run_bot():
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(TEXT & ~TEXT.command, submit_application))
    dispatcher.add_handler(CommandHandler("view", view_applications))

    updater.start_polling()
    updater.idle()

# Запускаем бота в отдельном потоке
threading.Thread(target=run_bot).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
