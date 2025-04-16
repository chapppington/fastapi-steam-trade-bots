from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.database import get_db
from app.schemas.bot import Bot, BotCreate, BotUpdate
from app.services.bot_service import BotService

router = APIRouter()

@router.post("/bots/", response_model=Bot)
async def create_bot(bot: BotCreate, db: AsyncSession = Depends(get_db)):
    db_bot = await BotService.get_bot_by_session_id(db, session_id=bot.session_id)
    if db_bot:
        raise HTTPException(status_code=400, detail="Bot with this session_id already exists")
    return await BotService.create_bot(db=db, bot=bot)

@router.get("/bots/", response_model=List[Bot])
async def read_bots(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    bots = await BotService.get_bots(db, skip=skip, limit=limit)
    return bots

@router.get("/bots/{bot_id}", response_model=Bot)
async def read_bot(bot_id: int, db: AsyncSession = Depends(get_db)):
    db_bot = await BotService.get_bot(db, bot_id=bot_id)
    if db_bot is None:
        raise HTTPException(status_code=404, detail="Bot not found")
    return db_bot

@router.put("/bots/{bot_id}", response_model=Bot)
async def update_bot(bot_id: int, bot: BotUpdate, db: AsyncSession = Depends(get_db)):
    db_bot = await BotService.update_bot(db, bot_id=bot_id, bot=bot)
    if db_bot is None:
        raise HTTPException(status_code=404, detail="Bot not found")
    return db_bot

@router.delete("/bots/{bot_id}")
async def delete_bot(bot_id: int, db: AsyncSession = Depends(get_db)):
    success = await BotService.delete_bot(db, bot_id=bot_id)
    if not success:
        raise HTTPException(status_code=404, detail="Bot not found")
    return {"message": "Bot deleted successfully"} 