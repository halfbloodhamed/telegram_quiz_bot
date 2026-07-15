from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.repositories.user_repository import UserRepository
from app.database.repositories.match_repository import MatchRepository
from app.keyboards.inline import get_back_to_menu_keyboard

router = Router()


@router.callback_query(F.data == "my_stats")
async def show_stats(callback: CallbackQuery, session: AsyncSession):
    """Show user statistics"""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    
    if not user:
        await callback.answer("Please /start first", show_alert=True)
        return
    
    win_rate = (user.wins / user.total_games * 100) if user.total_games > 0 else 0
    
    stats_text = (
        f"📊 Your Statistics\n\n"
        f"👤 Name: {user.display_name}\n"
        f"⭐ Rating: {user.rating}\n\n"
        f"🎮 Games Played: {user.total_games}\n"
        f"🏆 Wins: {user.wins}\n"
        f"💔 Losses: {user.losses}\n"
        f"📈 Win Rate: {win_rate:.1f}%\n"
    )
    
    await callback.message.edit_text(stats_text, reply_markup=get_back_to_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "leaderboard")
async def show_leaderboard(callback: CallbackQuery, session: AsyncSession):
    """Show global leaderboard"""
    user_repo = UserRepository(session)
    top_users = await user_repo.get_leaderboard(10)
    
    leaderboard_text = "🏆 Global Leaderboard\n\n"
    
    for idx, user in enumerate(top_users, 1):
        medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."
        leaderboard_text += (
            f"{medal} {user.display_name}\n"
            f"   ⭐ {user.rating} | 🎯 {user.total_games} games | 🏆 {user.wins} wins\n\n"
        )
    
    if not top_users:
        leaderboard_text += "No players yet. Be the first!"
    
    await callback.message.edit_text(leaderboard_text, reply_markup=get_back_to_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "match_history")
async def show_match_history(callback: CallbackQuery, session: AsyncSession):
    """Show match history"""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    
    if not user:
        await callback.answer("Please /start first", show_alert=True)
        return
    
    match_repo = MatchRepository(session)
    matches = await match_repo.get_by_user(user.id, 5)
    
    history_text = "📜 Recent Matches\n\n"
    
    for match in matches:
        is_player1 = match.player1_id == user.id
        my_score = match.player1_score if is_player1 else match.player2_score
        opp_score = match.player2_score if is_player1 else match.player1_score
        
        if match.winner_id == user.id:
            result = "🏆 WIN"
        elif match.winner_id is None:
            result = "🤝 DRAW"
        else:
            result = "💔 LOSS"
        
        rating_change = match.player1_rating_change if is_player1 else match.player2_rating_change
        rating_str = f"+{rating_change}" if rating_change > 0 else str(rating_change)
        
        history_text += (
            f"{result}\n"
            f"Score: {my_score} - {opp_score}\n"
            f"Rating: {rating_str}\n"
            f"Date: {match.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
        )
    
    if not matches:
        history_text += "No matches yet. Play your first game!"
    
    await callback.message.edit_text(history_text, reply_markup=get_back_to_menu_keyboard())
    await callback.answer()
