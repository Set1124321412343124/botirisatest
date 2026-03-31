from engine import IrisEngine
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession
from models import Ban, UserRank, ChatSettings
from utils import parse_duration, resolve_user
from datetime import datetime

engine = IrisEngine()

# Пример команды бана
@engine.register('бан', min_rank=2, description='Бан пользователя. Использование: бан [срок] @username [причина]')
async def ban_command(message: Message, args: str, session: AsyncSession):
    if not args:
        await message.reply("❌ Укажите пользователя и, возможно, срок.")
        return
    parts = args.split(maxsplit=2)
    duration = None
    target_identifier = None
    reason = None

    if parse_duration(parts[0]) is not None:
        duration = parse_duration(parts[0])
        target_identifier = parts[1] if len(parts) > 1 else None
        if len(parts) > 2:
            reason = parts[2]
    else:
        target_identifier = parts[0]
        if len(parts) > 1:
            reason = parts[1]

    if not target_identifier:
        await message.reply("❌ Не указан пользователь.")
        return

    target_id = await resolve_user(target_identifier, session, message.chat.id)
    if not target_id:
        await message.reply("❌ Не удалось определить пользователя.")
        return

    # Проверка прав (нельзя банить себя или вышестоящего)
    caller_rank = await session.get(UserRank, (message.chat.id, message.from_user.id))
    target_rank = await session.get(UserRank, (message.chat.id, target_id))
    if target_id == message.from_user.id:
        await message.reply("❌ Нельзя забанить себя.")
        return
    if caller_rank and target_rank and caller_rank.rank <= target_rank.rank:
        await message.reply("❌ Нельзя забанить пользователя с равным или более высоким рангом.")
        return

    try:
        await message.chat.ban(target_id)
    except Exception as e:
        await message.reply(f"❌ Ошибка бана: {e}")
        return

    ban_obj = Ban(
        chat_id=message.chat.id,
        user_id=target_id,
        expires_at=datetime.now() + duration if duration else None
    )
    session.add(ban_obj)
    await session.commit()

    duration_str = f" на {duration}" if duration else " навсегда"
    await message.reply(f"✅ Пользователь {target_id} забанен{duration_str}. Причина: {reason if reason else 'не указана'}.")

# Пример команды повышения
@engine.register('+модер', min_rank=4, description='Назначить модератором. Использование: +модер @username')
async def promote_command(message: Message, args: str, session: AsyncSession):
    if not args:
        await message.reply("❌ Укажите пользователя.")
        return
    target_identifier = args.split()[0]
    target_id = await resolve_user(target_identifier, session, message.chat.id)
    if not target_id:
        await message.reply("❌ Не удалось определить пользователя.")
        return

    # Определяем ранг по количеству восклицательных знаков в префиксе команды
    # В данном случае команда "+модер", но может быть "!!модер" и т.п.
    # Для упрощения: если команда "!!модер", то ранг 2 и т.д.
    # Но так как префикс убран, нужно это определять по тексту. Пока сделаем ранг 1.
    rank_level = 1

    caller_rank = await session.get(UserRank, (message.chat.id, message.from_user.id))
    if caller_rank and caller_rank.rank <= rank_level:
        await message.reply("❌ Вы не можете назначить ранг выше или равный вашему.")
        return

    rank_obj = await session.get(UserRank, (message.chat.id, target_id))
    if rank_obj:
        rank_obj.rank = rank_level
        rank_obj.assigned_by = message.from_user.id
    else:
        rank_obj = UserRank(
            chat_id=message.chat.id,
            user_id=target_id,
            rank=rank_level,
            assigned_by=message.from_user.id
        )
        session.add(rank_obj)
    await session.commit()
    await message.reply(f"✅ Пользователь {target_id} повышен до {rank_level} ранга.")