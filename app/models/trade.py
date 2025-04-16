from sqlalchemy import Column, String
from app.db.database import Base

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(String, primary_key=True)
    url = Column(String, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(String, nullable=False)
    completed_at = Column(String, nullable=True)
    response_data = Column(String, nullable=True) 