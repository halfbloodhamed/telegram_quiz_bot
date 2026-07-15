import asyncio
from typing import Dict, Optional
from aiogram import Bot
from app.database.models import Room, RoomState
from app.services.game_service import GameService
from app.services.redis_service import redis_service
from app.handlers.game import send_question_to_players, wait_for_answers, send_final_results
from app.config import settings
from app.utils.logger import logger


class GameScheduler:
    """Manages game flow and timing"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.active_games: Dict[str, asyncio.Task] = {}
    
    async def start_game(self, room: Room, session):
        """Start a new game"""
        if room.code in self.active_games:
            logger.warning(f"Game already running for room {room.code}")
            return
        
        # Create game task
        task = asyncio.create_task(self._run_game(room, session))
        self.active_games[room.code] = task
        
        # Clean up task when done
        task.add_done_callback(lambda t: self.active_games.pop(room.code, None))
    
    async def _run_game(self, room: Room, session):
        """Run the entire game flow"""
        try:
            game_service = GameService(session)
            
            # Notify players
            await self._notify_players(room, "🎮 Game starting in 3 seconds...")
            await asyncio.sleep(1)
            await self._notify_players(room, "3...")
            await asyncio.sleep(1)
            await self._notify_players(room, "2...")
            await asyncio.sleep(1)
            await self._notify_players(room, "1...")
            await asyncio.sleep(1)
            
            # Start game and get questions
            questions = await game_service.start_game(room)
            
            if not questions or len(questions) < settings.QUESTIONS_PER_GAME:
                await self._notify_players(room, "❌ Error: Not enough questions available")
                return
            
            # Update room state
            room.state = RoomState.PLAYING
            await session.commit()
            
            # Play through all questions
            for idx, question in enumerate(questions, 1):
                await send_question_to_players(self.bot, room, question, idx, len(questions))
                
                # Wait for answers or timeout
                player_ids = [p.user_id for p in room.players]
                await wait_for_answers(room.code, idx, player_ids)
                
                # Small delay before next question
                if idx < len(questions):
                    await asyncio.sleep(2)
            
            # Finish game
            await game_service.finish_game(room)
            await session.commit()
            
            # Reload room with updated player stats
            from app.database.repositories.room_repository import RoomRepository
            room_repo = RoomRepository(session)
            room = await room_repo.get_by_id(room.id)
            
            # Send final results
            await send_final_results(self.bot, room, room.players)
            
            logger.info(f"Game completed for room {room.code}")
            
        except Exception as e:
            logger.error(f"Error running game for room {room.code}: {e}", exc_info=True)
            await self._notify_players(room, "❌ An error occurred. Game cancelled.")
    
    async def _notify_players(self, room: Room, message: str):
        """Send notification to all players in room"""
        for player in room.players:
            try:
                await self.bot.send_message(player.user.telegram_id, message)
            except Exception as e:
                logger.error(f"Failed to notify player {player.user.telegram_id}: {e}")
    
    def cancel_game(self, room_code: str):
        """Cancel an active game"""
        if room_code in self.active_games:
            self.active_games[room_code].cancel()
            self.active_games.pop(room_code)
            logger.info(f"Game cancelled for room {room_code}")


# Global game scheduler (will be initialized in main.py)
game_scheduler: Optional[GameScheduler] = None


def set_game_scheduler(scheduler: GameScheduler):
    """Set the global game scheduler"""
    global game_scheduler
    game_scheduler = scheduler


def get_game_scheduler() -> Optional[GameScheduler]:
    """Get the global game scheduler"""
    return game_scheduler
