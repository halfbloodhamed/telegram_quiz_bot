import asyncio
from app.database.models import RoomState
from app.database.repositories.room_repository import RoomRepository
from app.services.game_service import GameService


class FakeSession:
    async def commit(self):
        return None


class FakeResult:
    def __init__(self, value):
        self.value = value

    def scalar_one_or_none(self):
        return self.value


class FakeRoomQuerySession(FakeSession):
    def __init__(self, room):
        self.room = room
        self.expired = False

    def expire_all(self):
        self.expired = True

    async def execute(self, statement):
        return FakeResult(self.room)


class FakePlayer:
    def __init__(self, room_id, user_id):
        self.id = len(self.__class__.__mro__) + 1
        self.room_id = room_id
        self.user_id = user_id
        self.user = None


class FakeRoom:
    def __init__(self, code="ABC123"):
        self.id = 1
        self.code = code
        self.state = RoomState.WAITING
        self.max_players = 2
        self.players = []


class FakeRoomRepository:
    def __init__(self, room):
        self.room = room

    async def get_by_code(self, code):
        return self.room


class FakePlayerRepository:
    def __init__(self, room):
        self.room = room

    async def get_by_room_and_user(self, room_id, user_id):
        return None

    async def get_by_room(self, room_id):
        return list(self.room.players)

    async def create(self, room_id, user_id):
        player = FakePlayer(room_id, user_id)
        self.room.players.append(player)
        return player


def test_join_room_returns_refreshed_room_with_two_players():
    room = FakeRoom()
    room.players.append(FakePlayer(1, 999))

    service = GameService(FakeSession())
    service.room_repo = FakeRoomRepository(room)
    service.player_repo = FakePlayerRepository(room)

    room, player, result = asyncio.run(service.join_room("abc123", 1001))

    assert result == "success"
    assert room is not None
    assert player is not None
    assert len(room.players) == 2


def test_room_repository_reloads_room_before_querying():
    room = FakeRoom()
    session = FakeRoomQuerySession(room)
    repo = RoomRepository(session)

    fetched_room = asyncio.run(repo.get_by_code("ABC123"))

    assert fetched_room is room
    assert session.expired is True
