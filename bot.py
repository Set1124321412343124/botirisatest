# -*- coding: utf-8 -*-
import asyncio
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update
from config import TOKEN
from commands import engine
from database import init_db
from scheduler import scheduler

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Подключаем роутеры с командами
engine.setup_handlers()
dp.include_router(engine.get_router())

# Обработчик вебхука
async def webhook(request):
    json_data = await request.json()
    update = Update(**json_data)
    await dp.feed_update(bot, update)
    return web.Response(text="OK")

# Действия при старте приложения
async def on_startup(app):
    await init_db()                     # создание таблиц БД
    asyncio.create_task(scheduler())    # запуск фоновой очистки наказаний

    # Устанавливаем вебхук
    hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME")
    if not hostname:
        # fallback для локальной разработки
        hostname = "your-app.onrender.com"
    webhook_url = f"https://{hostname}/webhook"
    await bot.set_webhook(webhook_url)
    print(f"Webhook set to {webhook_url}")

# Действия при остановке
async def on_shutdown(app):
    await bot.delete_webhook()
    await bot.session.close()

# Создаём aiohttp приложение
app = web.Application()
app.router.add_post('/webhook', webhook)
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    web.run_app(app, host='0.0.0.0', port=port)
