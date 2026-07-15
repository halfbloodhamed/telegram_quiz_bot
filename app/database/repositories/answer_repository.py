from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Answer


class AnswerRepository:
    """Answer repository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(
        self,
        player_id: int,
        question_id: int,
        user_id: int,
        selected_answer: Optional[str],
        correct_answer: str,
        is_correct: bool,
        response_time: Optional[float],
        score_earned: int
    ) -> Answer:
        """Create new answer"""
        answer = Answer(
            player_id=player_id,
            question_id=question_id,
            user_id=user_id,
            selected_answer=selected_answer,
            correct_answer=correct_answer,
            is_correct=is_correct,
            response_time=response_time,
            score_earned=score_earned
        )
        self.session.add(answer)
        await self.session.flush()
        return answer
    
    async def get_by_player_and_question(
        self,
        player_id: int,
        question_id: int
    ) -> Optional[Answer]:
        """Get answer by player and question"""
        result = await self.session.execute(
            select(Answer).where(
                Answer.player_id == player_id,
                Answer.question_id == question_id
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_player(self, player_id: int) -> List[Answer]:
        """Get all answers by player"""
        result = await self.session.execute(
            select(Answer).where(Answer.player_id == player_id)
        )
        return list(result.scalars().all())
