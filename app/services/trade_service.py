import json
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import uuid

from app.models.trade import Trade
from app.schemas.trade import TradeRequest, TradeResponse
from app.services.bot_service import BotService

from app.services.tradeoffer_service import TradeOfferService

class TradeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_trade(self, trade_request: TradeRequest) -> TradeResponse:
        trade_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        trade = Trade(
            id=trade_id,
            url=trade_request.url,
            status="pending",
            created_at=current_time
        )
        
        self.db.add(trade)
        await self.db.commit()
        
        return TradeResponse(
            id=trade_id,
            url=trade_request.url,
            status="pending",
            created_at=current_time,
            completed_at=None
        )

    async def get_trade(self, trade_id: str) -> Optional[TradeResponse]:
        stmt = select(Trade).where(Trade.id == trade_id)
        result = await self.db.execute(stmt)
        trade = result.scalar_one_or_none()
        
        if not trade:
            return None
            
        return trade

    async def list_trades(self) -> List[TradeResponse]:
        stmt = select(Trade).order_by(Trade.created_at.desc())
        result = await self.db.execute(stmt)
        trades = result.scalars().all()
        return trades

    async def process_trade(self, trade_id: str, url: str):
        try:
            # Get the next available bot using round-robin selection
            bot = await BotService.get_next_bot(self.db)
            if not bot:
                raise Exception("No bots available for processing trades")
            
            # Process the trade using the selected bot
            result = TradeOfferService.process_trade_offer(url, bot.session_id, bot.login_secure)
            
            # Get the trade from the database
            stmt = select(Trade).where(Trade.id == trade_id)
            query_result = await self.db.execute(stmt)
            trade = query_result.scalar_one()
            
            # Save trade response data
            trade.response_data = json.dumps(result)
            
            if result['success']:
                trade.status = "completed"
            else:
                trade.status = f"failed: {result.get('error', 'Unknown error')}"
            
            trade.completed_at = datetime.now().isoformat()
            await self.db.commit()
            
        except Exception as e:
            print(f"Error processing trade {trade_id}: {str(e)}")
            # Get the trade from the database
            stmt = select(Trade).where(Trade.id == trade_id)
            result = await self.db.execute(stmt)
            trade = result.scalar_one()
            
            # Update with error status
            trade.status = f"error: {str(e)}"
            trade.completed_at = datetime.now().isoformat()
            await self.db.commit() 