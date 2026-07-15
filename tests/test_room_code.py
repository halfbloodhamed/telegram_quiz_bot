import pytest
from app.utils.room_code import generate_room_code, validate_room_code


def test_generate_room_code_default_length():
    """Test room code generation with default length"""
    code = generate_room_code()
    assert len(code) == 6
    assert code.isalnum()


def test_generate_room_code_custom_length():
    """Test room code generation with custom length"""
    code = generate_room_code(8)
    assert len(code) == 8
    assert code.isalnum()


def test_generate_room_code_uniqueness():
    """Test that generated codes are likely unique"""
    codes = [generate_room_code() for _ in range(100)]
    assert len(set(codes)) == 100


def test_validate_room_code_valid():
    """Test validation of valid room code"""
    assert validate_room_code("ABC123") == True


def test_validate_room_code_wrong_length():
    """Test validation of code with wrong length"""
    assert validate_room_code("ABC") == False
    assert validate_room_code("ABC1234567") == False


def test_validate_room_code_invalid_chars():
    """Test validation of code with invalid characters"""
    assert validate_room_code("ABC-12") == False


def test_validate_room_code_empty():
    """Test validation of empty code"""
    assert validate_room_code("") == False
