from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.database.models import Question


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Get main menu keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎮 Create Room", callback_data="create_room")],
        [InlineKeyboardButton(text="🚪 Join Room", callback_data="join_room")],
        [InlineKeyboardButton(text="📊 My Stats", callback_data="my_stats")],
        [InlineKeyboardButton(text="🏆 Leaderboard", callback_data="leaderboard")],
        [InlineKeyboardButton(text="📜 Match History", callback_data="match_history")],
    ])


def get_question_keyboard(question: Question, room_code: str, question_num: int) -> InlineKeyboardMarkup:
    """Get question answer keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"A) {question.option_a}",
            callback_data=f"answer:{room_code}:{question_num}:A"
        )],
        [InlineKeyboardButton(
            text=f"B) {question.option_b}",
            callback_data=f"answer:{room_code}:{question_num}:B"
        )],
        [InlineKeyboardButton(
            text=f"C) {question.option_c}",
            callback_data=f"answer:{room_code}:{question_num}:C"
        )],
        [InlineKeyboardButton(
            text=f"D) {question.option_d}",
            callback_data=f"answer:{room_code}:{question_num}:D"
        )],
    ])


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Get cancel keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel")],
    ])


def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Get back to menu keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")],
    ])
