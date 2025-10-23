from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

print("🤖 Бот запущен!")

BOT_TOKEN = "8092588180:AAGJR1QrIqLgWBmZNxHEqb9f-Ou3YqLts7U"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📱 Открыть в приложении", web_app={"url": "https://your-website.com"})]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "Привет! Добро пожаловать в бота для проверки подарков.\n\n"
        "1. Нажмите кнопку ниже, скопируйте и вставьте свой username.\n"
        "2. Отправьте файл мини-приложению, получите результат проверки."
    )
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    
    print("✅ Бот запущен!")
    application.run_polling()

if __name__ == "__main__":
    main()
