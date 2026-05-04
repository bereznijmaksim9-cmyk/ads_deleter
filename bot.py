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

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER ---
async def handle(request):
    return web.Response(text="Bot is running!")

async def start_webserver():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
# ----------------------------------

@dp.message()
async def check_links_and_buttons(message: types.Message):
    # 1. Игнорируем только личные сообщения с ботом
    if message.chat.type == "private":
        return

    # 2. ПРОВЕРКА НА АДМИНА
    try:
        member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        if member.status in ["administrator", "creator"]:
            return
    except Exception:
        return

    # 3. ПОИСК ССЫЛОК И КНОПОК (теперь работает и для ботов!)
    has_link = False
    if message.entities:
        for entity in message.entities:
            if entity.type in ["url", "text_link"]:
                has_link = True
                break

    has_buttons = message.reply_markup is not None

    # 4. УДАЛЕНИЕ
    if has_link or has_buttons:
        try:
            await message.delete()
            logging.info(f"Удалено сообщение с кнопками/ссылкой от {message.from_user.id}")
        except Exception as e:
            logging.error(f"Не удалось удалить: {e}")

async def main():
    asyncio.create_task(start_webserver())
    print("Бот запущен и готов удалять кнопки...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
