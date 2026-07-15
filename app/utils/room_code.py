import random
import string
from app.config import settings


def generate_room_code(length: int = None) -> str:
    """Generate a random room code"""
    if length is None:
        length = settings.ROOM_CODE_LENGTH
    
    chars = string.ascii_uppercase.replace('O', '').replace('I', '') + string.digits.replace('0', '')
    return ''.join(random.choice(chars) for _ in range(length))


def validate_room_code(code: str) -> bool:
    """Validate room code format"""
    if not code or len(code) != settings.ROOM_CODE_LENGTH:
        return False
    return code.isalnum()
