import json
from typing import Optional, Dict, Any, List
from redis import asyncio as aioredis
from app.config import settings
from app.utils.logger import logger


class RedisService:
    """Redis service for room state management"""
    
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
    
    async def connect(self):
        """Connect to Redis"""
        self.redis = await aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
        logger.info("Connected to Redis")
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
            logger.info("Disconnected from Redis")
    
    async def set_room_state(self, room_code: str, state: Dict[str, Any], ttl: int = 3600):
        """Set room state"""
        key = f"room:{room_code}"
        await self.redis.setex(key, ttl, json.dumps(state))
    
    async def get_room_state(self, room_code: str) -> Optional[Dict[str, Any]]:
        """Get room state"""
        key = f"room:{room_code}"
        data = await self.redis.get(key)
        return json.loads(data) if data else None
    
    async def delete_room_state(self, room_code: str):
        """Delete room state"""
        key = f"room:{room_code}"
        await self.redis.delete(key)
    
    async def set_room_questions(self, room_code: str, question_ids: List[int]):
        """Set room questions"""
        key = f"room:{room_code}:questions"
        await self.redis.setex(key, 3600, json.dumps(question_ids))
    
    async def get_room_questions(self, room_code: str) -> Optional[List[int]]:
        """Get room questions"""
        key = f"room:{room_code}:questions"
        data = await self.redis.get(key)
        return json.loads(data) if data else None
    
    async def set_answer_submitted(self, room_code: str, question_idx: int, user_id: int):
        """Mark answer as submitted"""
        key = f"room:{room_code}:q{question_idx}:answer:{user_id}"
        await self.redis.setex(key, 300, "1")
    
    async def has_answer_submitted(self, room_code: str, question_idx: int, user_id: int) -> bool:
        """Check if answer was submitted"""
        key = f"room:{room_code}:q{question_idx}:answer:{user_id}"
        return await self.redis.exists(key) > 0
    
    async def set_timer(self, room_code: str, question_idx: int, expire_at: float):
        """Set question timer"""
        key = f"room:{room_code}:q{question_idx}:timer"
        await self.redis.setex(key, 60, str(expire_at))
    
    async def get_timer(self, room_code: str, question_idx: int) -> Optional[float]:
        """Get question timer"""
        key = f"room:{room_code}:q{question_idx}:timer"
        data = await self.redis.get(key)
        return float(data) if data else None


redis_service = RedisService()
