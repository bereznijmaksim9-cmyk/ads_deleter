import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiohttp import web

# Токен берем из настроек Render (Environment Variables)
TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# --- ЭТОТ БЛОК НУЖЕН ДЛЯ RENDER ---
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_webserver():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render сам подставит нужный порт в переменную PORT
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
# ----------------------------------

@dp.message()
async def check_links_and_buttons(message: types.Message):
    if message.chat.type == "private" or message.from_user.is_bot:
        return

    try:
        member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in ["administrator", "creator"]:
            return
    except Exception:
        return

    has_link = any(entity.type in ["url", "text_link"] for entity in (message.entities or []))
    has_buttons = message.reply_markup is not None

    if has_link or has_buttons:
        try:
            await message.delete()
        except Exception as e:
            logging.error(f"Error: {e}")

async def main():
    # Запускаем веб-сервер в фоне, чтобы Render не ругался
    asyncio.create_task(start_webserver())
    
    print("Бот запущен...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
