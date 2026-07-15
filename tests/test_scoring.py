import pytest
from app.utils.scoring import calculate_score, calculate_elo_change


def test_calculate_score_correct_fast():
    """Test score calculation for correct fast answer"""
    score = calculate_score(True, 5.0)
    assert score > 100
    assert score <= 107


def test_calculate_score_correct_slow():
    """Test score calculation for correct slow answer"""
    score = calculate_score(True, 14.0)
    assert score >= 100
    assert score <= 101


def test_calculate_score_incorrect():
    """Test score calculation for incorrect answer"""
    score = calculate_score(False, 5.0)
    assert score == 0


def test_calculate_score_incorrect_fast():
    """Test that speed doesn't matter for incorrect answers"""
    score = calculate_score(False, 1.0)
    assert score == 0


def test_elo_equal_ratings():
    """Test ELO calculation for equal ratings"""
    winner_change, loser_change = calculate_elo_change(1000, 1000)
    assert winner_change > 0
    assert loser_change < 0
    assert abs(winner_change) == abs(loser_change)


def test_elo_underdog_wins():
    """Test ELO calculation when lower rated player wins"""
    winner_change, loser_change = calculate_elo_change(900, 1100)
    assert winner_change > 16
    assert loser_change < -16


def test_elo_favorite_wins():
    """Test ELO calculation when higher rated player wins"""
    winner_change, loser_change = calculate_elo_change(1100, 900)
    assert winner_change < 16
    assert loser_change > -16
