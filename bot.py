from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext

print("🤖 Бот запущен!")

BOT_TOKEN = "8092588180:AAGJR1QrIqLgWBmZNxHEqb9f-Ou3YqLts7U"

def start(update: Update, context: CallbackContext):
    # Кнопка для мини-приложения
    keyboard = [
        [InlineKeyboardButton("📱 Открыть в приложении", web_app={"url": "https://your-website.com"})]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "Привет! Добро пожаловать в бота для проверки подарков.\n\n"
        "1. Нажмите кнопку ниже, скопируйте и вставьте свой username.\n"
        "2. Отправьте файл мини-приложению, получите результат проверки."
    )
    
    update.message.reply_text(welcome_text, reply_markup=reply_markup)

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    # Только команда /start
    dp.add_handler(CommandHandler("start", start))
    
    print("✅ Бот запущен!")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
