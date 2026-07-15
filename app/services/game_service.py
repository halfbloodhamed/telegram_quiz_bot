import asyncio
from datetime import datetime
from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Room, Player, Question, RoomState
from app.database.repositories.room_repository import RoomRepository
from app.database.repositories.player_repository import PlayerRepository
from app.database.repositories.question_repository import QuestionRepository
from app.database.repositories.answer_repository import AnswerRepository
from app.database.repositories.user_repository import UserRepository
from app.database.repositories.match_repository import MatchRepository
from app.services.redis_service import redis_service
from app.utils.room_code import generate_room_code
from app.utils.scoring import calculate_score, calculate_elo_change
from app.config import settings
from app.utils.logger import logger


class GameService:
    """Game logic service"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.room_repo = RoomRepository(session)
        self.player_repo = PlayerRepository(session)
        self.question_repo = QuestionRepository(session)
        self.answer_repo = AnswerRepository(session)
        self.user_repo = UserRepository(session)
        self.match_repo = MatchRepository(session)
    
    async def create_room(self, user_id: int) -> Tuple[Room, Player]:
        """Create a new room"""
        # Generate unique room code
        while True:
            code = generate_room_code()
            existing = await self.room_repo.get_by_code(code)
            if not existing:
                break
        
        # Create room
        room = await self.room_repo.create(code)
        
        # Add creator as player
        player = await self.player_repo.create(room.id, user_id)
        
        await self.session.commit()
        
        logger.info(f"Room created: {code} by user {user_id}")
        return room, player
    
    async def join_room(self, room_code: str, user_id: int) -> Tuple[Optional[Room], Optional[Player], str]:
        """Join a room"""
        room = await self.room_repo.get_by_code(room_code.upper())
        
        if not room:
            return None, None, "Room not found"
        
        if room.state != RoomState.WAITING:
            return None, None, "Room is not accepting players"
        
        # Check if already in room
        existing_player = await self.player_repo.get_by_room_and_user(room.id, user_id)
        if existing_player:
            return room, existing_player, "Already in room"
        
        # Check if room is full
        players = await self.player_repo.get_by_room(room.id)
        if len(players) >= room.max_players:
            return None, None, "Room is full"
        
        # Join room
        player = await self.player_repo.create(room.id, user_id)
        await self.session.commit()
        
        logger.info(f"User {user_id} joined room {room_code}")
        return room, player, "success"
    
    async def start_game(self, room: Room) -> List[Question]:
        """Start the game"""
        # Update room state
        room.state = RoomState.STARTING
        room.started_at = datetime.utcnow()
        await self.session.commit()
        
        # Get random questions
        questions = await self.question_repo.get_random_questions(settings.QUESTIONS_PER_GAME)
        
        # Store question IDs in Redis
        question_ids = [q.id for q in questions]
        await redis_service.set_room_questions(room.code, question_ids)
        
        logger.info(f"Game started in room {room.code}")
        return questions
    
    async def submit_answer(
        self,
        room: Room,
        player: Player,
        question: Question,
        selected_answer: Optional[str],
        response_time: Optional[float]
    ) -> int:
        """Submit an answer and calculate score"""
        is_correct = selected_answer == question.correct_answer if selected_answer else False
        
        # Calculate score
        if response_time is not None and is_correct:
            score_earned = calculate_score(True, response_time)
        else:
            score_earned = 0
        
        # Save answer
        await self.answer_repo.create(
            player_id=player.id,
            question_id=question.id,
            user_id=player.user_id,
            selected_answer=selected_answer,
            correct_answer=question.correct_answer,
            is_correct=is_correct,
            response_time=response_time,
            score_earned=score_earned
        )
        
        # Update player stats
        await self.player_repo.update_score(player, score_earned, is_correct, response_time)
        await self.session.commit()
        
        return score_earned
    
    async def finish_game(self, room: Room):
        """Finish the game and save results"""
        room.state = RoomState.FINISHED
        room.finished_at = datetime.utcnow()
        
        # Get all players
        players = await self.player_repo.get_by_room(room.id)
        
        if len(players) != 2:
            await self.session.commit()
            return
        
        p1, p2 = players[0], players[1]
        
        # Determine winner
        winner_id = None
        if p1.score > p2.score:
            winner_id = p1.user_id
            winner_user = await self.user_repo.get_by_id(p1.user_id)
            loser_user = await self.user_repo.get_by_id(p2.user_id)
        elif p2.score > p1.score:
            winner_id = p2.user_id
            winner_user = await self.user_repo.get_by_id(p2.user_id)
            loser_user = await self.user_repo.get_by_id(p1.user_id)
        else:
            winner_user = None
            loser_user = None
        
        # Calculate ELO changes
        p1_rating_change = 0
        p2_rating_change = 0
        
        if winner_user and loser_user:
            winner_change, loser_change = calculate_elo_change(
                winner_user.rating,
                loser_user.rating
            )
            
            if winner_id == p1.user_id:
                p1_rating_change = winner_change
                p2_rating_change = loser_change
                await self.user_repo.update_stats(winner_user, True, winner_change)
                await self.user_repo.update_stats(loser_user, False, loser_change)
            else:
                p2_rating_change = winner_change
                p1_rating_change = loser_change
                await self.user_repo.update_stats(winner_user, True, winner_change)
                await self.user_repo.update_stats(loser_user, False, loser_change)
        else:
            # Draw
            u1 = await self.user_repo.get_by_id(p1.user_id)
            u2 = await self.user_repo.get_by_id(p2.user_id)
            await self.user_repo.update_stats(u1, False, 0)
            await self.user_repo.update_stats(u2, False, 0)
        
        # Calculate duration
        duration = None
        if room.started_at:
            duration = int((room.finished_at - room.started_at).total_seconds())
        
        # Save match history
        await self.match_repo.create(
            room_id=room.id,
            player1_id=p1.user_id,
            player2_id=p2.user_id,
            player1_score=p1.score,
            player2_score=p2.score,
            player1_correct=p1.correct_answers,
            player2_correct=p2.correct_answers,
            player1_incorrect=p1.incorrect_answers,
            player2_incorrect=p2.incorrect_answers,
            winner_id=winner_id,
            total_questions=settings.QUESTIONS_PER_GAME,
            duration_seconds=duration,
            player1_rating_change=p1_rating_change,
            player2_rating_change=p2_rating_change
        )
        
        await self.session.commit()
        
        # Clean up Redis
        await redis_service.delete_room_state(room.code)
        
        logger.info(f"Game finished in room {room.code}")
