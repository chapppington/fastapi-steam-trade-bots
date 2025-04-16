from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import declarative_base

# Use a single database for both trades and bots
DATABASE_URL = "sqlite+aiosqlite:///database.db"
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()

# Import models to ensure they are registered with Base
from app.models.trade import Trade
from app.models.bot import Bot

async def get_db():
    async with async_session() as session:
        yield session 