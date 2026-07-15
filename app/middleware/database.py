from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from app.database.connection import get_db


class DatabaseMiddleware(BaseMiddleware):
    """Middleware to inject database session"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        async for session in get_db():
            data["session"] = session
            return await handler(event, data)
