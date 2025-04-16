from pydantic import BaseModel

class BotBase(BaseModel):
    session_id: str
    login_secure: str

class BotCreate(BotBase):
    pass

class BotUpdate(BotBase):
    pass

class Bot(BotBase):
    id: int

    class Config:
        from_attributes = True 