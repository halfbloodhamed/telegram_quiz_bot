from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.repositories.question_repository import QuestionRepository, CategoryRepository
from app.database.repositories.user_repository import UserRepository
from app.database.repositories.room_repository import RoomRepository
from app.database.models import DifficultyLevel
from app.config import settings
from app.utils.logger import logger

router = Router()


class AddQuestionStates(StatesGroup):
    waiting_for_question = State()
    waiting_for_options = State()
    waiting_for_answer = State()


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in settings.admin_ids_list


@router.message(Command("admin"))
async def admin_panel(message: Message):
    """Show admin panel"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ You don't have admin access")
        return
    
    admin_text = (
        "🔧 Admin Panel\n\n"
        "Available commands:\n"
        "/addquestion - Add a new question\n"
        "/stats - View bot statistics\n"
        "/broadcast <message> - Send message to all users\n"
        "/listrooms - List active rooms"
    )
    
    await message.answer(admin_text)


@router.message(Command("stats"))
async def admin_stats(message: Message, session: AsyncSession):
    """Show bot statistics"""
    if not is_admin(message.from_user.id):
        return
    
    user_repo = UserRepository(session)
    question_repo = QuestionRepository(session)
    room_repo = RoomRepository(session)
    
    total_users = await user_repo.get_total_users()
    total_questions = await question_repo.get_total_questions()
    total_rooms = await room_repo.get_total_rooms()
    
    stats_text = (
        f"📊 Bot Statistics\n\n"
        f"👥 Total Users: {total_users}\n"
        f"❓ Total Questions: {total_questions}\n"
        f"🏠 Total Rooms: {total_rooms}\n"
    )
    
    await message.answer(stats_text)


@router.message(Command("listrooms"))
async def list_rooms(message: Message, session: AsyncSession):
    """List active rooms"""
    if not is_admin(message.from_user.id):
        return
    
    room_repo = RoomRepository(session)
    rooms = await room_repo.get_active_rooms()
    
    rooms_text = "🏠 Active Rooms\n\n"
    
    for room in rooms:
        rooms_text += (
            f"Code: {room.code}\n"
            f"State: {room.state.value}\n"
            f"Players: {len(room.players)}/{room.max_players}\n\n"
        )
    
    if not rooms:
        rooms_text += "No active rooms"
    
    await message.answer(rooms_text)


@router.message(Command("broadcast"))
async def broadcast_message(message: Message, session: AsyncSession):
    """Broadcast message to all users"""
    if not is_admin(message.from_user.id):
        return
    
    text = message.text.replace("/broadcast", "").strip()
    
    if not text:
        await message.answer("Usage: /broadcast <message>")
        return
    
    user_repo = UserRepository(session)
    # This is simplified - in production, paginate through users
    await message.answer("Broadcasting... (feature requires implementation)")
