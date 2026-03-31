import re
from typing import Dict, Callable
from aiogram import Router, types
from sqlalchemy.ext.asyncio import AsyncSession
from models import UserRank, ChatSettings
from database import get_session
from config import PREFIXES

class IrisEngine:
    def __init__(self):
        self.commands: Dict[str, dict] = {}
        self.router = Router()

    def register(self, command_name: str, min_rank: int = 0, description: str = ""):
        def decorator(func: Callable):
            self.commands[command_name] = {
                'func': func,
                'rank': min_rank,
                'desc': description
            }
            return func
        return decorator

    async def _check_rank(self, chat_id: int, user_id: int, required_rank: int, session: AsyncSession) -> bool:
        if required_rank == 0:
            return True
        rank_obj = await session.get(UserRank, (chat_id, user_id))
        user_rank = rank_obj.rank if rank_obj else 0
        return user_rank >= required_rank

    async def _process_command(self, message: types.Message, command_text: str):
        parts = command_text.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else None

        if cmd not in self.commands:
            return

        cmd_info = self.commands[cmd]
        required_rank = cmd_info['rank']

        async with get_session() as session:
            if not await self._check_rank(message.chat.id, message.from_user.id, required_rank, session):
                await message.reply(f"❌ Недостаточно прав. Требуется ранг {required_rank}.")
                return

            try:
                await cmd_info['func'](message, args, session)
            except Exception as e:
                await message.reply(f"❌ Ошибка: {e}")

    def setup_handlers(self):
        @self.router.message()
        async def handle_all(message: types.Message):
            if not message.text:
                return
            for prefix in PREFIXES:
                if message.text.startswith(prefix):
                    command_text = message.text[len(prefix):].strip()
                    await self._process_command(message, command_text)
                    break

    def get_router(self):
        return self.router