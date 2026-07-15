from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.repositories.user_repository import UserRepository
from app.services.game_service import GameService
from app.scheduler.game_scheduler import get_game_scheduler
from app.keyboards.inline import get_cancel_keyboard, get_back_to_menu_keyboard
from app.utils.room_code import validate_room_code
from app.utils.logger import logger
from aiogram import Bot

router = Router()


class RoomStates(StatesGroup):
    waiting_for_code = State()


@router.callback_query(F.data == "create_room")
async def create_room(callback: CallbackQuery, session: AsyncSession):
    """Create a new room"""
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    
    if not user:
        await callback.answer("Please /start first", show_alert=True)
        return
    
    game_service = GameService(session)
    room, player = await game_service.create_room(user.id)
    
    room_text = (
        f"🎮 Room Created!\n\n"
        f"📋 Room Code: `{room.code}`\n\n"
        f"👥 Players: 1/{room.max_players}\n"
        f"⏳ Waiting for opponent...\n\n"
        f"Share the room code with your friend to start the game!"
    )
    
    await callback.message.edit_text(room_text, reply_markup=get_back_to_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "join_room")
async def join_room_prompt(callback: CallbackQuery, state: FSMContext):
    """Prompt for room code"""
    await state.set_state(RoomStates.waiting_for_code)
    
    text = (
        f"🚪 Join a Room\n\n"
        f"Please enter the 6-character room code:"
    )
    
    await callback.message.edit_text(text, reply_markup=get_cancel_keyboard())
    await callback.answer()


@router.message(RoomStates.waiting_for_code)
async def process_room_code(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    """Process room code input"""
    room_code = message.text.strip().upper()
    
    if not validate_room_code(room_code):
        await message.answer("❌ Invalid room code format. Please try again.")
        return
    
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    
    if not user:
        await message.answer("Please /start first")
        await state.clear()
        return
    
    game_service = GameService(session)
    room, player, result = await game_service.join_room(room_code, user.id)
    
    if result != "success":
        await message.answer(f"❌ {result}", reply_markup=get_back_to_menu_keyboard())
        await state.clear()
        return
    
    await state.clear()

    # Reload the room and player list from the database so the join flow uses fresh state
    room = await game_service.room_repo.get_by_id(room.id)
    players = await game_service.player_repo.get_by_room(room.id)

    # Check if room is full and can start
    if len(players) >= room.max_players:
        # Notify both players
        for player in players:
            try:
                await bot.send_message(
                    player.user.telegram_id,
                    f"✅ Opponent joined! Game starting soon..."
                )
            except Exception as e:
                logger.error(f"Failed to notify player: {e}")
        
        # Start the game
        scheduler = get_game_scheduler()
        if scheduler:
            await scheduler.start_game(room, session)
        else:
            logger.error("Game scheduler not initialized")
    else:
        text = (
            f"✅ Joined Room {room_code}!\n\n"
            f"⏳ Waiting for game to start..."
        )
        await message.answer(text, reply_markup=get_back_to_menu_keyboard())


@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    """Cancel current action"""
    await state.clear()
    await callback.message.edit_text(
        "❌ Cancelled",
        reply_markup=get_back_to_menu_keyboard()
    )
    await callback.answer()
