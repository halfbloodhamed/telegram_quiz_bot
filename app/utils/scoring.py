from app.config import settings


def calculate_score(is_correct: bool, response_time: float) -> int:
    """Calculate score based on correctness and speed"""
    if not is_correct:
        return 0
    
    time_bonus = max(0, settings.QUESTION_TIME_LIMIT - response_time)
    bonus_points = int(time_bonus * settings.TIME_BONUS_MULTIPLIER)
    
    return settings.BASE_SCORE + bonus_points


def calculate_elo_change(winner_rating: int, loser_rating: int, k: int = 32) -> tuple[int, int]:
    """Calculate ELO rating changes"""
    expected_winner = 1 / (1 + 10 ** ((loser_rating - winner_rating) / 400))
    expected_loser = 1 / (1 + 10 ** ((winner_rating - loser_rating) / 400))
    
    winner_change = int(k * (1 - expected_winner))
    loser_change = int(k * (0 - expected_loser))
    
    return winner_change, loser_change
