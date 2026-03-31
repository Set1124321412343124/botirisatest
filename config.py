import os
TOKEN = os.getenv('BOT_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')
PREFIXES = ["!", ".", "/", "Ирис ", "Ириска "]

if not TOKEN:
    raise ValueError("BOT_TOKEN не установлен в переменных окружения")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL не установлен в переменных окружения")
