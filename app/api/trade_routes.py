from typing import List
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.trade import TradeRequest, TradeResponse
from app.services.trade_service import TradeService

router = APIRouter()

@router.post("/trade", response_model=TradeResponse)
async def create_trade(
    trade_request: TradeRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    trade_service = TradeService(db)
    trade_response = await trade_service.create_trade(trade_request)
    
    # Start background process
    background_tasks.add_task(
        trade_service.process_trade,
        trade_response.id,
        trade_request.url
    )
    
    return trade_response

@router.get("/trade/{trade_id}", response_model=TradeResponse)
async def get_trade(trade_id: str, db: AsyncSession = Depends(get_db)):
    trade_service = TradeService(db)
    trade = await trade_service.get_trade(trade_id)
    
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    return trade

@router.get("/trades", response_model=List[TradeResponse])
async def list_trades(db: AsyncSession = Depends(get_db)):
    trade_service = TradeService(db)
    return await trade_service.list_trades() 