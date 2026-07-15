from typing import Optional, List
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import User


class UserRepository:
    """User repository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create(
        self,
        telegram_id: int,
        username: Optional[str],
        display_name: str
    ) -> User:
        """Create new user"""
        user = User(
            telegram_id=telegram_id,
            username=username,
            display_name=display_name
        )
        self.session.add(user)
        await self.session.flush()
        return user
    
    async def get_or_create(
        self,
        telegram_id: int,
        username: Optional[str],
        display_name: str
    ) -> User:
        """Get existing user or create new one"""
        user = await self.get_by_telegram_id(telegram_id)
        if not user:
            user = await self.create(telegram_id, username, display_name)
        return user
    
    async def update_stats(
        self,
        user: User,
        won: bool,
        rating_change: int = 0
    ) -> User:
        """Update user statistics"""
        user.total_games += 1
        if won:
            user.wins += 1
        else:
            user.losses += 1
        user.rating += rating_change
        await self.session.flush()
        return user
    
    async def get_leaderboard(self, limit: int = 10) -> List[User]:
        """Get top users by rating"""
        result = await self.session.execute(
            select(User)
            .where(User.total_games > 0)
            .order_by(desc(User.rating))
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_total_users(self) -> int:
        """Get total number of users"""
        result = await self.session.execute(
            select(func.count(User.id))
        )
        return result.scalar_one()
