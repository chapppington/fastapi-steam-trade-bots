from typing import Optional
from pydantic import BaseModel

class TradeRequest(BaseModel):
    url: str

class TradeResponse(BaseModel):
    id: str
    url: str
    status: str
    created_at: str
    completed_at: Optional[str] = None
    response_data: Optional[str] = None
    
    class Config:
        from_attributes = True 