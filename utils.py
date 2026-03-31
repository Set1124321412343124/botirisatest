import re
from datetime import datetime, timedelta
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

async def resolve_user(identifier: str, session: AsyncSession, chat_id: int):
    """
    Упрощённый поиск пользователя по @username или по reply.
    Для полноты нужно парсить ссылки, но пока так.
    """
    if identifier.startswith('@'):
        username = identifier[1:]
        # Здесь нужно вызвать Telegram API для получения пользователя по username
        # В aiogram: await bot.get_chat(username)
        # Но чтобы не усложнять, пока возвращаем заглушку
        return None
    # Если identifier — это число, то возможно user_id
    if identifier.isdigit():
        return int(identifier)
    return None

def parse_duration(text: str) -> timedelta | None:
    text = text.strip().lower()
    match = re.match(r'(\d+)\s*(минут|минута|минуты|час|часа|часов|день|дня|дней|сутки|суток|недел|месяц|месяца|месяцев|год|года|лет)', text)
    if not match:
        return None
    num = int(match.group(1))
    unit = match.group(2)
    if unit.startswith('минут'):
        return timedelta(minutes=num)
    elif unit.startswith('час'):
        return timedelta(hours=num)
    elif unit.startswith('день') or unit.startswith('сутк'):
        return timedelta(days=num)
    elif unit.startswith('недел'):
        return timedelta(weeks=num)
    elif unit.startswith('месяц'):
        return timedelta(days=num*30)
    elif unit.startswith('год'):
        return timedelta(days=num*365)
    return None