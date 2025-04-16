from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.bot import Bot
from app.schemas.bot import BotCreate, BotUpdate
from typing import List, Optional
from datetime import datetime

class BotService:
    @staticmethod
    async def create_bot(db: AsyncSession, bot: BotCreate) -> Bot:
        db_bot = Bot(
            session_id=bot.session_id,
            login_secure=bot.login_secure
        )
        db.add(db_bot)
        await db.commit()
        await db.refresh(db_bot)
        return db_bot

    @staticmethod
    async def get_bot(db: AsyncSession, bot_id: int) -> Optional[Bot]:
        result = await db.execute(select(Bot).filter(Bot.id == bot_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_bot_by_session_id(db: AsyncSession, session_id: str) -> Optional[Bot]:
        result = await db.execute(select(Bot).filter(Bot.session_id == session_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_bots(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Bot]:
        result = await db.execute(select(Bot).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def update_bot(db: AsyncSession, bot_id: int, bot: BotUpdate) -> Optional[Bot]:
        result = await db.execute(select(Bot).filter(Bot.id == bot_id))
        db_bot = result.scalar_one_or_none()
        if db_bot:
            for key, value in bot.model_dump().items():
                setattr(db_bot, key, value)
            await db.commit()
            await db.refresh(db_bot)
        return db_bot

    @staticmethod
    async def delete_bot(db: AsyncSession, bot_id: int) -> bool:
        result = await db.execute(select(Bot).filter(Bot.id == bot_id))
        db_bot = result.scalar_one_or_none()
        if db_bot:
            await db.delete(db_bot)
            await db.commit()
            return True
        return False

    @staticmethod
    async def get_next_bot(db: AsyncSession) -> Optional[Bot]:
        """Get the next available bot using round-robin selection based on last_used_at"""
        # Get the bot that was used least recently
        result = await db.execute(
            select(Bot)
            .order_by(Bot.last_used_at.asc())
            .limit(1)
        )
        bot = result.scalar_one_or_none()
        
        if bot:
            # Update the last_used_at timestamp
            bot.last_used_at = datetime.utcnow()
            await db.commit()
            await db.refresh(bot)
            
        return bot 