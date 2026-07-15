from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker
)
from app.config import settings


class DatabaseManager:
    """Database connection manager"""
    
    def __init__(self):
        engine_kwargs = {
            "echo": not settings.is_production,
        }
        if settings.DATABASE_URL.startswith("postgresql"):
            engine_kwargs.update({
                "pool_pre_ping": True,
                "pool_size": 20,
                "max_overflow": 10,
            })

        self.engine: AsyncEngine = create_async_engine(
            settings.DATABASE_URL,
            **engine_kwargs,
        )
        
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session"""
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def close(self):
        """Close database connection"""
        await self.engine.dispose()


# Global database manager instance
db_manager = DatabaseManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session"""
    async for session in db_manager.get_session():
        yield session
