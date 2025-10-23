import os
import asyncio
import traceback
from aiohttp import web, ClientSession
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import WebAppInfo

# 🔑 Токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден! Убедись, что переменная установлена в Render.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 📩 Команда /start
@dp.message(CommandStart())
async def start(message: types.Message):
    kb = InlineKeyboardBuilder()
    # Кнопка для Telegram Mini App
    kb.button(
        text="📱 Открыть в приложении",
        web_app=WebAppInfo(url="https://trepall.github.io/draineeer/")
    )
    kb.adjust(1)

    text = (
        "Привет! Добро пожаловать в бота для проверки подарков.\n\n"
        "1. Нажмите кнопку ниже, скопируйте и вставьте свой username.\n"
        "2. Отправьте файл мини-приложению, получите результат проверки."
    )

    await message.answer(
        text=text,
        reply_markup=kb.as_markup()
    )

# 🌐 Простейший веб-сервер
async def handle_root(request):
    return web.Response(text="Portals bot is alive!")

async def start_web_server():
    app = web.Application()
    app.add_routes([web.get("/", handle_root)])
    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"🌐 Web server running on port {port}")

# ♻️ Запуск Telegram-бота
async def run_bot():
    while True:
        try:
            print("✅ Bot is running...")
            await dp.start_polling(bot)
        except Exception as e:
            print("⚠️ Ошибка:", e)
            traceback.print_exc()
            print("♻️ Перезапуск через 5 секунд...")
            await asyncio.sleep(5)

# 🕐 Keep-alive (пингует Render URL)
async def keep_alive():
    url = os.getenv("RENDER_EXTERNAL_URL")
    if not url:
        print("⚠️ Переменная RENDER_EXTERNAL_URL не найдена, keep-alive не активен.")
        return
    print(f"🔄 Keep-alive включен, пингует {url}")
    while True:
        try:
            async with ClientSession() as session:
                async with session.get(url) as resp:
                    print(f"🌍 Keep-alive ping: {resp.status}")
        except Exception as e:
            print("⚠️ Ошибка keep-alive:", e)
        await asyncio.sleep(300)  # каждые 5 минут

# 🚀 Запуск всех процессов
async def main():
    await asyncio.gather(start_web_server(), run_bot(), keep_alive())

if __name__ == "__main__":
    asyncio.run(main())
