from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    # Bot Configuration
    BOT_TOKEN: str
    ADMIN_IDS: str = ""
    
    # Database Configuration
    DATABASE_URL: str
    
    # Redis Configuration
    REDIS_URL: str
    
    # Game Configuration
    QUESTIONS_PER_GAME: int = 10
    QUESTION_TIME_LIMIT: int = 15
    ROOM_CODE_LENGTH: int = 6
    MAX_PLAYERS_PER_ROOM: int = 2
    COUNTDOWN_SECONDS: int = 3
    
    # Scoring Configuration
    BASE_SCORE: int = 100
    TIME_BONUS_MULTIPLIER: float = 0.5
    
    # Environment
    ENVIRONMENT: str = "production"
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    @property
    def admin_ids_list(self) -> List[int]:
        """Parse admin IDs from comma-separated string"""
        if not self.ADMIN_IDS:
            return []
        return [int(id_.strip()) for id_ in self.ADMIN_IDS.split(",") if id_.strip()]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT.lower() == "production"


settings = Settings()
