from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.database.models import Room, RoomState, Player


class RoomRepository:
    """Room repository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_code(self, code: str) -> Optional[Room]:
        """Get room by code with players loaded"""
        self.session.expire_all() if hasattr(self.session, "expire_all") else None
        result = await self.session.execute(
            select(Room)
            .options(selectinload(Room.players).selectinload(Player.user))
            .where(Room.code == code)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, room_id: int) -> Optional[Room]:
        """Get room by ID with players loaded"""
        self.session.expire_all() if hasattr(self.session, "expire_all") else None
        result = await self.session.execute(
            select(Room)
            .options(selectinload(Room.players).selectinload(Player.user))
            .where(Room.id == room_id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, code: str, max_players: int = 2) -> Room:
        """Create new room"""
        room = Room(
            code=code,
            state=RoomState.WAITING,
            max_players=max_players
        )
        self.session.add(room)
        await self.session.flush()
        return room
    
    async def update_state(self, room: Room, state: RoomState) -> Room:
        """Update room state"""
        room.state = state
        await self.session.flush()
        return room
    
    async def delete(self, room: Room):
        """Delete room"""
        await self.session.delete(room)
        await self.session.flush()
    
    async def get_active_rooms(self) -> List[Room]:
        """Get all active rooms (waiting or playing)"""
        result = await self.session.execute(
            select(Room)
            .options(selectinload(Room.players).selectinload(Player.user))
            .where(Room.state.in_([RoomState.WAITING, RoomState.STARTING, RoomState.PLAYING]))
        )
        return list(result.scalars().all())
    
    async def get_total_rooms(self) -> int:
        """Get total number of rooms"""
        result = await self.session.execute(
            select(func.count(Room.id))
        )
        return result.scalar_one()
