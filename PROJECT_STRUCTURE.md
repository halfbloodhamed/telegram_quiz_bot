# Project Structure

## Overview
This document explains the complete project structure of the Telegram Quiz Game Bot.

## Directory Tree

```
quiz_telegram_bot/
├── app/                                # Main application directory
│   ├── __init__.py                    # Package initialization
│   ├── main.py                        # Application entry point
│   ├── config.py                      # Configuration and settings
│   │
│   ├── database/                      # Database layer
│   │   ├── __init__.py
│   │   ├── models.py                  # SQLAlchemy models
│   │   ├── connection.py              # Database connection manager
│   │   └── repositories/              # Data access layer
│   │       ├── __init__.py
│   │       ├── user_repository.py     # User CRUD operations
│   │       ├── room_repository.py     # Room CRUD operations
│   │       ├── player_repository.py   # Player CRUD operations
│   │       ├── question_repository.py # Question CRUD operations
│   │       ├── answer_repository.py   # Answer CRUD operations
│   │       └── match_repository.py    # Match history operations
│   │
│   ├── handlers/                      # Bot command handlers
│   │   ├── __init__.py
│   │   ├── start.py                   # /start command and main menu
│   │   ├── room.py                    # Room creation and joining
│   │   ├── game.py                    # Game play logic
│   │   ├── stats.py                   # Statistics and leaderboard
│   │   └── admin.py                   # Admin commands
│   │
│   ├── services/                      # Business logic layer
│   │   ├── __init__.py
│   │   ├── game_service.py            # Core game logic
│   │   └── redis_service.py           # Redis operations
│   │
│   ├── scheduler/                     # Game flow automation
│   │   ├── __init__.py
│   │   └── game_scheduler.py          # Automated game flow manager
│   │
│   ├── keyboards/                     # Telegram UI
│   │   ├── __init__.py
│   │   └── inline.py                  # Inline keyboard definitions
│   │
│   ├── middleware/                    # Bot middleware
│   │   ├── __init__.py
│   │   └── database.py                # Database session injection
│   │
│   └── utils/                         # Utility functions
│       ├── __init__.py
│       ├── logger.py                  # Logging configuration
│       ├── room_code.py               # Room code generation
│       └── scoring.py                 # Score and ELO calculation
│
├── alembic/                           # Database migrations
│   ├── versions/                      # Migration files
│   │   └── .gitkeep
│   ├── env.py                         # Alembic environment
│   └── script.py.mako                 # Migration template
│
├── scripts/                           # Utility scripts
│   ├── __init__.py
│   ├── seed_questions.py              # Seed database with questions
│   ├── setup.ps1                      # Windows setup script
│   ├── create_migration.sh            # Unix migration script
│   └── create_migration.ps1           # Windows migration script
│
├── tests/                             # Test suite
│   ├── __init__.py
│   ├── test_scoring.py                # Scoring logic tests
│   ├── test_room_code.py              # Room code tests
│   └── test_game_service.py           # Game service tests
│
├── .dockerignore                      # Docker ignore file
├── .env.example                       # Environment template
├── .gitignore                         # Git ignore file
├── alembic.ini                        # Alembic configuration
├── CONTRIBUTING.md                    # Contribution guidelines
├── docker-compose.yml                 # Docker orchestration
├── Dockerfile                         # Bot container definition
├── PROJECT_STRUCTURE.md               # This file
├── pytest.ini                         # Pytest configuration
├── QUICKSTART.md                      # Quick start guide
├── README.md                          # Main documentation
└── requirements.txt                   # Python dependencies
```

## Component Breakdown

### Database Layer (`app/database/`)

**models.py** - Defines all database tables:
- User: Player profiles and statistics
- Room: Game rooms
- Player: Links users to rooms
- Question: Question pool
- Answer: Player answers
- MatchHistory: Game results
- Category: Question categories
- And more...

**repositories/** - Data access patterns:
- Each repository handles CRUD for one model
- Async/await throughout
- SQLAlchemy ORM with type hints

### Handlers (`app/handlers/`)

**start.py** - Entry point:
- `/start` command
- User registration
- Main menu display

**room.py** - Room management:
- Create room with unique code
- Join room by code
- Room validation

**game.py** - Game play:
- Answer submission
- Question display
- Result calculation

**stats.py** - Statistics:
- Player stats
- Leaderboard
- Match history

**admin.py** - Admin functions:
- Bot statistics
- Room listing
- Broadcasting

### Services (`app/services/`)

**game_service.py** - Core game logic:
- Room creation/joining
- Game start/finish
- Answer processing
- Score calculation
- ELO updates

**redis_service.py** - State management:
- Room state
- Question timers
- Answer tracking
- Fast temporary storage

### Scheduler (`app/scheduler/`)

**game_scheduler.py** - Automated game flow:
- Countdown timer
- Question delivery
- Answer waiting
- Results distribution
- Game cleanup

### Utilities (`app/utils/`)

**logger.py** - Logging:
- Centralized logging
- Configurable levels
- Console output

**room_code.py** - Code generation:
- Random alphanumeric codes
- Validation
- No confusing characters (0, O, I)

**scoring.py** - Calculations:
- Score based on speed
- ELO rating updates
- Win/loss tracking

### Keyboards (`app/keyboards/`)

**inline.py** - Telegram UI:
- Main menu
- Question answers
- Navigation buttons
- Inline keyboards

### Middleware (`app/middleware/`)

**database.py** - Session injection:
- Provides DB session to handlers
- Auto-commit on success
- Auto-rollback on error

## Data Flow

### User Registration
```
User sends /start
  → start.py handler
  → UserRepository.get_or_create()
  → Database insert/select
  → Return user object
  → Show main menu
```

### Room Creation
```
User clicks "Create Room"
  → room.py handler
  → GameService.create_room()
  → Generate unique code
  → RoomRepository.create()
  → PlayerRepository.create()
  → Return room code
```

### Game Flow
```
Room is full
  → GameScheduler.start_game()
  → Send countdown
  → GameService.start_game()
  → Get random questions
  → For each question:
    - Send to players
    - Start timer in Redis
    - Wait for answers
    - Calculate scores
  → GameService.finish_game()
  → Update ratings
  → Save match history
  → Send final results
```

### Answer Submission
```
Player clicks answer button
  → game.py callback handler
  → Check Redis if already answered
  → GameService.submit_answer()
  → Calculate score with time bonus
  → Save to database
  → Update player stats
  → Mark as answered in Redis
```

## Database Schema

### Core Tables

**users**
- id (PK)
- telegram_id (unique)
- username
- display_name
- wins, losses, total_games
- rating (ELO)
- timestamps

**rooms**
- id (PK)
- code (unique, 6 chars)
- state (waiting/starting/playing/finished)
- current_question
- timestamps

**players**
- id (PK)
- room_id (FK → rooms)
- user_id (FK → users)
- score
- correct_answers, incorrect_answers
- response times

**questions**
- id (PK)
- category_id (FK → categories)
- text
- option_a, option_b, option_c, option_d
- correct_answer (A/B/C/D)
- difficulty

**answers**
- id (PK)
- player_id (FK → players)
- question_id (FK → questions)
- selected_answer
- is_correct
- response_time
- score_earned

**match_history**
- id (PK)
- room_id (FK → rooms)
- player1_id, player2_id (FK → users)
- scores, correct counts
- winner_id
- rating changes
- duration

## Redis Keys

```
room:{code}                      - Room state JSON
room:{code}:questions            - Question IDs array
room:{code}:q{idx}:answer:{uid}  - Answer submitted flag
room:{code}:q{idx}:timer         - Timer expiration timestamp
```

## Configuration

### Environment Variables (.env)
- BOT_TOKEN: Telegram bot token
- DATABASE_URL: PostgreSQL connection
- REDIS_URL: Redis connection
- QUESTIONS_PER_GAME: Default 10
- QUESTION_TIME_LIMIT: Default 15 seconds
- ADMIN_IDS: Comma-separated admin user IDs

### Game Settings
- Room code length: 6 characters
- Max players per room: 2
- Base score: 100 points
- Time bonus: Up to 7.5 points
- Starting ELO: 1000
- ELO K-factor: 32

## Deployment

### Docker Compose Services
1. **postgres** - PostgreSQL 16
   - Persistent volume
   - Health checks
   
2. **redis** - Redis 7
   - Persistent volume
   - Health checks
   
3. **bot** - Python application
   - Depends on postgres + redis
   - Auto-restarts
   - Runs migrations on startup

### Startup Sequence
1. Docker Compose starts postgres and redis
2. Health checks ensure they're ready
3. Bot container starts
4. Alembic runs migrations
5. Bot connects to services
6. Game scheduler initializes
7. Bot starts polling Telegram

## Testing

### Test Structure
- **Unit tests**: Individual functions
- **Integration tests**: Full workflows
- **Fixtures**: Mock data and sessions

### Running Tests
```bash
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest --cov=app          # With coverage
pytest tests/test_scoring.py  # Specific file
```

## Extending the Bot

### Adding a New Question Category
1. Add questions to `seed_questions.py`
2. Run seed script
3. Category auto-created

### Adding a New Command
1. Create handler function
2. Register route with `@router.message()` or `@router.callback_query()`
3. Include router in `main.py`

### Adding a New Database Table
1. Add model to `models.py`
2. Create repository
3. Generate migration: `alembic revision --autogenerate`
4. Review and apply: `alembic upgrade head`

## Security Considerations

- No secrets in code
- Environment variables for config
- SQL injection prevention (ORM)
- Input validation (room codes, etc.)
- Admin-only commands
- Rate limiting (built into Telegram)

## Performance

### Scalability
- Async/await throughout
- Connection pooling
- Redis for fast state
- Hundreds of concurrent games supported

### Optimizations
- Eager loading (selectinload)
- Indexed database fields
- Redis for temporary data
- Efficient queries

---

For setup instructions, see QUICKSTART.md
For development guidelines, see CONTRIBUTING.md
For user documentation, see README.md
