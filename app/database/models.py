from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional
from sqlalchemy import (
    BigInteger, String, Integer, Float, Boolean, Text,
    DateTime, ForeignKey, Index, Enum, JSON
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class RoomState(str, PyEnum):
    """Room states"""
    WAITING = "waiting"
    STARTING = "starting"
    PLAYING = "playing"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class DifficultyLevel(str, PyEnum):
    """Question difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class PowerUpType(str, PyEnum):
    """Power-up types"""
    FIFTY_FIFTY = "fifty_fifty"
    SKIP = "skip"
    EXTRA_TIME = "extra_time"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Statistics
    wins: Mapped[int] = mapped_column(Integer, default=0)
    losses: Mapped[int] = mapped_column(Integer, default=0)
    total_games: Mapped[int] = mapped_column(Integer, default=0)
    rating: Mapped[int] = mapped_column(Integer, default=1000)  # ELO rating
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    players: Mapped[List["Player"]] = relationship("Player", back_populates="user")
    answers: Mapped[List["Answer"]] = relationship("Answer", back_populates="user")
    friends: Mapped[List["Friendship"]] = relationship("Friendship", foreign_keys="Friendship.user_id", back_populates="user")


class Room(Base):
    """Room model"""
    __tablename__ = "rooms"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
    state: Mapped[RoomState] = mapped_column(Enum(RoomState), default=RoomState.WAITING)
    current_question: Mapped[int] = mapped_column(Integer, default=0)
    max_players: Mapped[int] = mapped_column(Integer, default=2)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Relationships
    players: Mapped[List["Player"]] = relationship("Player", back_populates="room", cascade="all, delete-orphan")
    match_history: Mapped[Optional["MatchHistory"]] = relationship("MatchHistory", back_populates="room", uselist=False)


class Player(Base):
    """Player model (links users to rooms)"""
    __tablename__ = "players"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    room_id: Mapped[int] = mapped_column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    score: Mapped[int] = mapped_column(Integer, default=0)
    correct_answers: Mapped[int] = mapped_column(Integer, default=0)
    incorrect_answers: Mapped[int] = mapped_column(Integer, default=0)
    no_answers: Mapped[int] = mapped_column(Integer, default=0)
    total_response_time: Mapped[float] = mapped_column(Float, default=0.0)
    is_ready: Mapped[bool] = mapped_column(Boolean, default=False)
    
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    room: Mapped["Room"] = relationship("Room", back_populates="players")
    user: Mapped["User"] = relationship("User", back_populates="players")
    answers: Mapped[List["Answer"]] = relationship("Answer", back_populates="player")
    
    __table_args__ = (
        Index("idx_player_room_user", "room_id", "user_id", unique=True),
    )


class Category(Base):
    """Question category model"""
    __tablename__ = "categories"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    questions: Mapped[List["Question"]] = relationship("Question", back_populates="category")


class Question(Base):
    """Question model"""
    __tablename__ = "questions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    category_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("categories.id", ondelete="SET NULL"))
    text: Mapped[str] = mapped_column(Text, nullable=False)
    option_a: Mapped[str] = mapped_column(String(500), nullable=False)
    option_b: Mapped[str] = mapped_column(String(500), nullable=False)
    option_c: Mapped[str] = mapped_column(String(500), nullable=False)
    option_d: Mapped[str] = mapped_column(String(500), nullable=False)
    correct_answer: Mapped[str] = mapped_column(String(1), nullable=False)  # A, B, C, or D
    difficulty: Mapped[DifficultyLevel] = mapped_column(Enum(DifficultyLevel), default=DifficultyLevel.MEDIUM)
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    explanation: Mapped[Optional[str]] = mapped_column(Text)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="questions")
    answers: Mapped[List["Answer"]] = relationship("Answer", back_populates="question")


class Answer(Base):
    """Answer model (tracks player answers)"""
    __tablename__ = "answers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    player_id: Mapped[int] = mapped_column(Integer, ForeignKey("players.id", ondelete="CASCADE"))
    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    
    selected_answer: Mapped[Optional[str]] = mapped_column(String(1))  # A, B, C, D, or None
    correct_answer: Mapped[str] = mapped_column(String(1), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    response_time: Mapped[Optional[float]] = mapped_column(Float)  # seconds
    score_earned: Mapped[int] = mapped_column(Integer, default=0)
    
    answered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    player: Mapped["Player"] = relationship("Player", back_populates="answers")
    question: Mapped["Question"] = relationship("Question", back_populates="answers")
    user: Mapped["User"] = relationship("User", back_populates="answers")
    
    __table_args__ = (
        Index("idx_answer_player_question", "player_id", "question_id", unique=True),
    )


class MatchHistory(Base):
    """Match history model"""
    __tablename__ = "match_history"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    room_id: Mapped[int] = mapped_column(Integer, ForeignKey("rooms.id", ondelete="CASCADE"), unique=True)
    winner_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"))
    
    player1_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    player1_score: Mapped[int] = mapped_column(Integer, default=0)
    player1_correct: Mapped[int] = mapped_column(Integer, default=0)
    player1_incorrect: Mapped[int] = mapped_column(Integer, default=0)
    player1_rating_change: Mapped[int] = mapped_column(Integer, default=0)
    
    player2_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    player2_score: Mapped[int] = mapped_column(Integer, default=0)
    player2_correct: Mapped[int] = mapped_column(Integer, default=0)
    player2_incorrect: Mapped[int] = mapped_column(Integer, default=0)
    player2_rating_change: Mapped[int] = mapped_column(Integer, default=0)
    
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    room: Mapped["Room"] = relationship("Room", back_populates="match_history")


class Friendship(Base):
    """Friendship model"""
    __tablename__ = "friendships"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    friend_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="friends")
    
    __table_args__ = (
        Index("idx_friendship_unique", "user_id", "friend_id", unique=True),
    )


class DailyChallenge(Base):
    """Daily challenge model"""
    __tablename__ = "daily_challenges"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime, unique=True, nullable=False, index=True)
    question_ids: Mapped[List[int]] = mapped_column(JSON, nullable=False)
    category_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("categories.id", ondelete="SET NULL"))
    difficulty: Mapped[DifficultyLevel] = mapped_column(Enum(DifficultyLevel), default=DifficultyLevel.MEDIUM)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class UserPowerUp(Base):
    """User power-ups inventory"""
    __tablename__ = "user_powerups"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    powerup_type: Mapped[PowerUpType] = mapped_column(Enum(PowerUpType), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_user_powerup", "user_id", "powerup_type", unique=True),
    )
