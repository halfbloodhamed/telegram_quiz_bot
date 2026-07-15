from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database.models import Player


class PlayerRepository:
    """Player repository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, player_id: int) -> Optional[Player]:
        """Get player by ID"""
        result = await self.session.execute(
            select(Player)
            .options(selectinload(Player.user), selectinload(Player.room))
            .where(Player.id == player_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_room_and_user(self, room_id: int, user_id: int) -> Optional[Player]:
        """Get player by room and user"""
        result = await self.session.execute(
            select(Player)
            .options(selectinload(Player.user))
            .where(Player.room_id == room_id, Player.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_room(self, room_id: int) -> List[Player]:
        """Get all players in room"""
        result = await self.session.execute(
            select(Player)
            .options(selectinload(Player.user))
            .where(Player.room_id == room_id)
        )
        return list(result.scalars().all())
    
    async def create(self, room_id: int, user_id: int) -> Player:
        """Create new player"""
        player = Player(room_id=room_id, user_id=user_id)
        self.session.add(player)
        await self.session.flush()
        return player
    
    async def update_score(
        self,
        player: Player,
        score_earned: int,
        is_correct: bool,
        response_time: Optional[float] = None
    ) -> Player:
        """Update player score and stats"""
        player.score += score_earned
        if is_correct:
            player.correct_answers += 1
        else:
            player.incorrect_answers += 1
        
        if response_time is not None:
            player.total_response_time += response_time
        else:
            player.no_answers += 1
        
        await self.session.flush()
        return player
