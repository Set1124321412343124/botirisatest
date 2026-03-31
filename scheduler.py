import asyncio
from datetime import datetime
from sqlalchemy import select, delete
from models import Warn, Mute, Ban
from database import async_session
from aiogram import Bot
from config import TOKEN

bot = Bot(token=TOKEN)

async def expire_warns():
    async with async_session() as session:
        result = await session.execute(select(Warn).where(Warn.expires_at <= datetime.now()))
        warns = result.scalars().all()
        for warn in warns:
            await session.delete(warn)
        await session.commit()

async def expire_mutes():
    async with async_session() as session:
        result = await session.execute(select(Mute).where(Mute.expires_at <= datetime.now()))
        mutes = result.scalars().all()
        for mute in mutes:
            try:
                await bot.restrict_chat_member(mute.chat_id, mute.user_id,
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True
                )
            except:
                pass
            await session.delete(mute)
        await session.commit()

async def expire_bans():
    async with async_session() as session:
        result = await session.execute(select(Ban).where(Ban.expires_at <= datetime.now()))
        bans = result.scalars().all()
        for ban in bans:
            try:
                await bot.unban_chat_member(ban.chat_id, ban.user_id)
            except:
                pass
            await session.delete(ban)
        await session.commit()

async def scheduler():
    while True:
        await expire_warns()
        await expire_mutes()
        await expire_bans()
        await asyncio.sleep(60)