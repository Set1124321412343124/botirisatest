import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import TOKEN
from commands import engine
from database import init_db
from scheduler import scheduler

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    await init_db()
    engine.setup_handlers()
    dp.include_router(engine.get_router())
    asyncio.create_task(scheduler())
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())