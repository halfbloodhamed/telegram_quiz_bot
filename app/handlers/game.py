import asyncio
import time
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import RoomState
from app.database.repositories.room_repository import RoomRepository
from app.database.repositories.user_repository import UserRepository
from app.database.repositories.player_repository import PlayerRepository
from app.database.repositories.question_repository import QuestionRepository
from app.services.game_service import GameService
from app.services.redis_service import redis_service
from app.keyboards.inline import get_question_keyboard, get_back_to_menu_keyboard
from app.config import settings
from app.utils.logger import logger

router = Router()


async def send_question_to_players(
    bot: Bot,
    room,
    question,
    question_num: int,
    total_questions: int
):
    """Send question to all players in room"""
    players = room.players
    
    question_text = (
        f"❓ Question {question_num}/{total_questions}\n\n"
        f"{question.text}\n\n"
        f"⏱️ Time: {settings.QUESTION_TIME_LIMIT} seconds"
    )
    
    keyboard = get_question_keyboard(question, room.code, question_num)
    
    # Set timer in Redis
    started_at = time.time()
    expire_at = started_at + settings.QUESTION_TIME_LIMIT
    await redis_service.set_timer(room.code, question_num, expire_at)
    await redis_service.set_question_state(room.code, question_num, started_at, expire_at)
    
    for player in players:
        try:
            await bot.send_message(
                player.user.telegram_id,
                question_text,
                reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"Failed to send question to user {player.user.telegram_id}: {e}")


async def wait_for_answers(room_code: str, question_num: int, player_ids: list):
    """Wait for all answers or timeout"""
    start_time = time.time()
    
    while time.time() - start_time < settings.QUESTION_TIME_LIMIT:
        # Check if all players answered
        all_answered = True
        for player_id in player_ids:
            if not await redis_service.has_answer_submitted(room_code, question_num, player_id):
                all_answered = False
                break
        
        if all_answered:
            return True
        
        await asyncio.sleep(0.5)
    
    return False


def parse_answer_callback_data(callback_data: str):
    """Parse answer callback data into room code, question number, and selected answer."""
    parts = callback_data.split(":")
    if len(parts) != 4 or parts[0] != "answer":
        raise ValueError("Invalid answer format")

    _, room_code, question_str, selected = parts
    return room_code, int(question_str), selected


@router.callback_query(F.data.startswith("answer:"))
async def handle_answer(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    """Handle player answer"""
    try:
        room_code, question_num, selected = parse_answer_callback_data(callback.data)
    except (ValueError, IndexError):
        await callback.answer("Invalid answer format", show_alert=True)
        return

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)

    if not user:
        await callback.answer("User not found", show_alert=True)
        return

    room_repo = RoomRepository(session)
    room = await room_repo.get_by_code(room_code)
    if not room:
        await callback.answer("Room not found", show_alert=True)
        return

    player_repo = PlayerRepository(session)
    player = await player_repo.get_by_room_and_user(room.id, user.id)
    if not player:
        await callback.answer("You are not a participant in this room", show_alert=True)
        return

    if await redis_service.has_answer_submitted(room_code, question_num, player.user_id):
        await callback.answer("Answer already recorded", show_alert=True)
        return

    question_ids = await redis_service.get_room_questions(room_code)
    if not question_ids or question_num - 1 >= len(question_ids):
        await callback.answer("Question not found", show_alert=True)
        return

    question_repo = QuestionRepository(session)
    question = await question_repo.get_by_id(question_ids[question_num - 1])
    if not question:
        await callback.answer("Question not found", show_alert=True)
        return

    question_state = await redis_service.get_question_state(room_code, question_num)
    response_time = None
    if question_state:
        started_at = question_state.get("started_at")
        if started_at is not None:
            response_time = round(time.time() - started_at, 2)

    game_service = GameService(session)
    await game_service.submit_answer(
        room=room,
        player=player,
        question=question,
        selected_answer=selected,
        response_time=response_time,
    )

    await redis_service.set_answer_submitted(room_code, question_num, player.user_id)
    await redis_service.set_answer_data(
        room_code,
        question_num,
        player.user_id,
        {
            "selected_answer": selected,
            "response_time": response_time,
        },
    )

    await callback.answer("✅ Answer submitted!")
    await callback.message.edit_reply_markup(reply_markup=None)


async def send_final_results(bot: Bot, room, players):
    """Send final game results to all players"""
    if len(players) != 2:
        return
    
    p1, p2 = players[0], players[1]
    
    # Determine winner
    if p1.score > p2.score:
        winner = p1
        loser = p2
        result_p1 = "🏆 YOU WON!"
        result_p2 = "💔 You Lost"
    elif p2.score > p1.score:
        winner = p2
        loser = p1
        result_p1 = "💔 You Lost"
        result_p2 = "🏆 YOU WON!"
    else:
        result_p1 = "🤝 DRAW"
        result_p2 = "🤝 DRAW"
    
    # Player 1 stats
    avg_time_p1 = p1.total_response_time / (p1.correct_answers + p1.incorrect_answers) if (p1.correct_answers + p1.incorrect_answers) > 0 else 0
    accuracy_p1 = (p1.correct_answers / settings.QUESTIONS_PER_GAME) * 100 if settings.QUESTIONS_PER_GAME > 0 else 0
    
    results_text_p1 = (
        f"{result_p1}\n\n"
        f"📊 Final Results\n\n"
        f"You: {p1.score} points\n"
        f"Opponent: {p2.score} points\n\n"
        f"✅ Correct: {p1.correct_answers}\n"
        f"❌ Incorrect: {p1.incorrect_answers}\n"
        f"⏭️ No Answer: {p1.no_answers}\n"
        f"🎯 Accuracy: {accuracy_p1:.1f}%\n"
        f"⏱️ Avg Time: {avg_time_p1:.1f}s\n"
    )
    
    # Player 2 stats
    avg_time_p2 = p2.total_response_time / (p2.correct_answers + p2.incorrect_answers) if (p2.correct_answers + p2.incorrect_answers) > 0 else 0
    accuracy_p2 = (p2.correct_answers / settings.QUESTIONS_PER_GAME) * 100 if settings.QUESTIONS_PER_GAME > 0 else 0
    
    results_text_p2 = (
        f"{result_p2}\n\n"
        f"📊 Final Results\n\n"
        f"You: {p2.score} points\n"
        f"Opponent: {p1.score} points\n\n"
        f"✅ Correct: {p2.correct_answers}\n"
        f"❌ Incorrect: {p2.incorrect_answers}\n"
        f"⏭️ No Answer: {p2.no_answers}\n"
        f"🎯 Accuracy: {accuracy_p2:.1f}%\n"
        f"⏱️ Avg Time: {avg_time_p2:.1f}s\n"
    )
    
    try:
        await bot.send_message(
            p1.user.telegram_id,
            results_text_p1,
            reply_markup=get_back_to_menu_keyboard()
        )
    except Exception as e:
        logger.error(f"Failed to send results to player 1: {e}")
    
    try:
        await bot.send_message(
            p2.user.telegram_id,
            results_text_p2,
            reply_markup=get_back_to_menu_keyboard()
        )
    except Exception as e:
        logger.error(f"Failed to send results to player 2: {e}")
