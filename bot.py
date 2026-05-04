import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# Токен лучше хранить в переменных окружения, но для теста оставляем здесь
# ВАЖНО: Если ты публиковал этот токен в открытом доступе, лучше перевыпусти его у BotFather
TOKEN = "8785433173:AAF2hw39tpyEVwX11zyi1gEIeXtunE8WSIA"

bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

@dp.message()
async def check_links_and_buttons(message: types.Message):
    # 1. Пропускаем проверку, если это личные сообщения с ботом
    if message.chat.type == "private":
        return

    # 2. ПРОВЕРКА НА АДМИНА
    # Бот спрашивает у Телеграма статус того, кто отправил сообщение
    try:
        member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        # Если статус пользователя — администратор или владелец (creator), выходим из функции
        if member.status in ["administrator", "creator"]:
            return
    except Exception as e:
        logging.error(f"Ошибка проверки статуса: {e}")
        # Если не удалось проверить статус, на всякий случай не удаляем
        return

    # 3. ЛОГИКА ПОИСКА СПАМА (для всех остальных: ботов и обычных юзеров)
    
    # Проверяем наличие ссылок
    has_link = False
    if message.entities:
        for entity in message.entities:
            if entity.type in ["url", "text_link"]:
                has_link = True
                break

    # Проверяем наличие кнопок (reply_markup)
    has_buttons = message.reply_markup is not None

    # 4. УДАЛЕНИЕ
    if has_link or has_buttons:
        try:
            await message.delete()
            logging.info(f"Удалено спам-сообщение от {message.from_user.id}")
        except Exception as e:
            logging.error(f"Не удалось удалить сообщение: {e}")

async def main():
    print("Бот запущен и защищает чат от спама...")
    # Удаляем старые сообщения, которые пришли, пока бот был выключен
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
