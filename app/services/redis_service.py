import json
import time
from typing import Optional, Dict, Any, List
from redis import asyncio as aioredis
from app.config import settings
from app.utils.logger import logger


class RedisService:
    """Redis service for room state management"""
    
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self.memory_store: Dict[str, Any] = {}
        self.memory_ttl: Dict[str, float] = {}

    def _is_memory_mode(self) -> bool:
        return bool(settings.REDIS_URL) and settings.REDIS_URL.startswith("memory://")

    def _purge_expired(self):
        now = time.time()
        expired_keys = [
            key for key, expires_at in self.memory_ttl.items()
            if expires_at is not None and now >= expires_at
        ]
        for key in expired_keys:
            self.memory_store.pop(key, None)
            self.memory_ttl.pop(key, None)

    async def connect(self):
        """Connect to Redis"""
        if self._is_memory_mode():
            self.memory_store.clear()
            self.memory_ttl.clear()
            logger.info("Using in-memory Redis fallback")
            return

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
        self.memory_store.clear()
        self.memory_ttl.clear()

    async def _store_value(self, key: str, value: Any, ttl: int):
        if self.redis is not None:
            await self.redis.setex(key, ttl, value)
            return

        self._purge_expired()
        self.memory_store[key] = value
        self.memory_ttl[key] = time.time() + ttl

    async def _get_value(self, key: str) -> Optional[Any]:
        if self.redis is not None:
            return await self.redis.get(key)

        self._purge_expired()
        return self.memory_store.get(key)

    async def _delete_key(self, key: str):
        if self.redis is not None:
            await self.redis.delete(key)
            return

        self._purge_expired()
        self.memory_store.pop(key, None)
        self.memory_ttl.pop(key, None)

    async def _exists(self, key: str) -> bool:
        if self.redis is not None:
            return await self.redis.exists(key) > 0

        self._purge_expired()
        return key in self.memory_store
    
    async def set_room_state(self, room_code: str, state: Dict[str, Any], ttl: int = 3600):
        """Set room state"""
        key = f"room:{room_code}"
        await self._store_value(key, json.dumps(state), ttl)
    
    async def get_room_state(self, room_code: str) -> Optional[Dict[str, Any]]:
        """Get room state"""
        key = f"room:{room_code}"
        data = await self._get_value(key)
        return json.loads(data) if data else None
    
    async def delete_room_state(self, room_code: str):
        """Delete room state"""
        key = f"room:{room_code}"
        await self._delete_key(key)
    
    async def set_room_questions(self, room_code: str, question_ids: List[int]):
        """Set room questions"""
        key = f"room:{room_code}:questions"
        await self._store_value(key, json.dumps(question_ids), 3600)
    
    async def get_room_questions(self, room_code: str) -> Optional[List[int]]:
        """Get room questions"""
        key = f"room:{room_code}:questions"
        data = await self._get_value(key)
        return json.loads(data) if data else None
    
    async def set_answer_submitted(self, room_code: str, question_idx: int, user_id: int):
        """Mark answer as submitted"""
        key = f"room:{room_code}:q{question_idx}:answer:{user_id}"
        await self._store_value(key, "1", 300)
    
    async def has_answer_submitted(self, room_code: str, question_idx: int, user_id: int) -> bool:
        """Check if answer was submitted"""
        key = f"room:{room_code}:q{question_idx}:answer:{user_id}"
        return await self._exists(key)
    
    async def set_timer(self, room_code: str, question_idx: int, expire_at: float):
        """Set question timer"""
        key = f"room:{room_code}:q{question_idx}:timer"
        await self._store_value(key, str(expire_at), 60)

    async def set_question_state(self, room_code: str, question_idx: int, started_at: float, expire_at: float):
        """Store question timing metadata"""
        key = f"room:{room_code}:q{question_idx}:state"
        payload = json.dumps({"started_at": started_at, "expire_at": expire_at})
        await self._store_value(key, payload, 60)

    async def get_question_state(self, room_code: str, question_idx: int) -> Optional[Dict[str, Any]]:
        """Get question timing metadata"""
        key = f"room:{room_code}:q{question_idx}:state"
        data = await self._get_value(key)
        return json.loads(data) if data else None

    async def set_answer_data(self, room_code: str, question_idx: int, user_id: int, answer_data: Dict[str, Any]):
        """Store the submitted answer payload for a player"""
        key = f"room:{room_code}:q{question_idx}:answer:{user_id}:data"
        await self._store_value(key, json.dumps(answer_data), 300)

    async def get_answer_data(self, room_code: str, question_idx: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get the stored answer payload for a player"""
        key = f"room:{room_code}:q{question_idx}:answer:{user_id}:data"
        data = await self._get_value(key)
        return json.loads(data) if data else None
    
    async def get_timer(self, room_code: str, question_idx: int) -> Optional[float]:
        """Get question timer"""
        key = f"room:{room_code}:q{question_idx}:timer"
        data = await self._get_value(key)
        return float(data) if data else None


redis_service = RedisService()
