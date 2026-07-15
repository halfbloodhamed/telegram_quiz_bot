from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.repositories.user_repository import UserRepository
from app.keyboards.inline import get_main_menu_keyboard, get_back_to_menu_keyboard
from app.utils.logger import logger

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, session: AsyncSession):
    """Handle /start command"""
    user_repo = UserRepository(session)
    
    telegram_id = message.from_user.id
    username = message.from_user.username
    display_name = message.from_user.full_name
    
    user = await user_repo.get_or_create(telegram_id, username, display_name)
    await session.commit()
    
    logger.info(f"User {telegram_id} started the bot")
    
    welcome_text = (
        f"👋 Welcome to Quiz Battle, {user.display_name}!\n\n"
        f"🎮 Challenge your friends in real-time quiz battles!\n\n"
        f"📊 Your Stats:\n"
        f"⭐ Rating: {user.rating}\n"
        f"🏆 Wins: {user.wins}\n"
        f"💔 Losses: {user.losses}\n"
        f"🎯 Total Games: {user.total_games}\n\n"
        f"Choose an option below:"
    )
    
    await message.answer(welcome_text, reply_markup=get_main_menu_keyboard())


@router.callback_query(F.data == "main_menu")
async def show_main_menu(callback: CallbackQuery, session: AsyncSession):
    """Show main menu"""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    
    if not user:
        await callback.answer("Please /start first", show_alert=True)
        return
    
    menu_text = (
        f"📊 Your Stats:\n"
        f"⭐ Rating: {user.rating}\n"
        f"🏆 Wins: {user.wins}\n"
        f"💔 Losses: {user.losses}\n"
        f"🎯 Total Games: {user.total_games}\n\n"
        f"Choose an option:"
    )
    
    await callback.message.edit_text(menu_text, reply_markup=get_main_menu_keyboard())
    await callback.answer()
