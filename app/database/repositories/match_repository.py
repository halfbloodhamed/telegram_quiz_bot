from typing import Optional, List
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import MatchHistory


class MatchRepository:
    """Match history repository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(
        self,
        room_id: int,
        player1_id: int,
        player2_id: int,
        player1_score: int,
        player2_score: int,
        player1_correct: int,
        player2_correct: int,
        player1_incorrect: int,
        player2_incorrect: int,
        winner_id: Optional[int],
        total_questions: int,
        duration_seconds: Optional[int],
        player1_rating_change: int = 0,
        player2_rating_change: int = 0
    ) -> MatchHistory:
        """Create new match history"""
        match = MatchHistory(
            room_id=room_id,
            player1_id=player1_id,
            player2_id=player2_id,
            player1_score=player1_score,
            player2_score=player2_score,
            player1_correct=player1_correct,
            player2_correct=player2_correct,
            player1_incorrect=player1_incorrect,
            player2_incorrect=player2_incorrect,
            winner_id=winner_id,
            total_questions=total_questions,
            duration_seconds=duration_seconds,
            player1_rating_change=player1_rating_change,
            player2_rating_change=player2_rating_change
        )
        self.session.add(match)
        await self.session.flush()
        return match
    
    async def get_by_user(self, user_id: int, limit: int = 10) -> List[MatchHistory]:
        """Get match history for user"""
        result = await self.session.execute(
            select(MatchHistory)
            .where(
                (MatchHistory.player1_id == user_id) |
                (MatchHistory.player2_id == user_id)
            )
            .order_by(desc(MatchHistory.created_at))
            .limit(limit)
        )
        return list(result.scalars().all())
