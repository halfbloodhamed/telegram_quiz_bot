# 🎮 Telegram Multiplayer Quiz Game

A production-ready real-time multiplayer quiz game bot for Telegram with comprehensive features including room-based matchmaking, ELO rating system, leaderboards, and match history.

## ✨ Features

### Core Gameplay
- **Room-based Multiplayer**: Create and join private rooms with unique 6-character codes
- **Real-time Quiz Battles**: Face off against opponents in timed quiz matches
- **10 Questions per Game**: Carefully selected from a diverse question pool
- **15-Second Timer**: Fast-paced gameplay with time-based scoring
- **Instant Results**: See scores and answers after each question

### User Features
- **Auto Registration**: Users are automatically registered on first `/start`
- **Player Statistics**: Track wins, losses, total games, and accuracy
- **ELO Rating System**: Competitive ranking based on performance
- **Match History**: Review past games with detailed statistics
- **Global Leaderboard**: Compete for the top spot

### Technical Features
- **Async Architecture**: Supports hundreds of concurrent games
- **Redis State Management**: Fast room state and timer handling
- **PostgreSQL Database**: Robust data storage with SQLAlchemy ORM
- **Database Migrations**: Alembic for version-controlled schema changes
- **Docker Support**: One-command deployment with Docker Compose
- **Type Hints**: Fully typed codebase for better maintainability
- **Comprehensive Logging**: Track all game events and errors

### Question System
- **100+ Questions**: Diverse question pool across multiple categories
- **5 Categories**: Programming, Science, History, Sports, Movies
- **3 Difficulty Levels**: Easy, Medium, Hard
- **No Repeats**: Questions never repeat within a single match
- **Extensible**: Easy to add new questions via admin commands

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Telegram Bot Token (get from [@BotFather](https://t.me/botfather))

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd quiz_telegram_bot
```

2. **Configure environment**
```bash
cp .env.example .env
```

Edit `.env` and add your bot token:
```env
BOT_TOKEN=your_telegram_bot_token_here
ADMIN_IDS=your_telegram_user_id
```

3. **Start with Docker Compose**
```bash
docker-compose up -d
```

4. **Seed the database with questions**
```bash
docker-compose exec bot python scripts/seed_questions.py
```

5. **Check logs**
```bash
docker-compose logs -f bot
```

That's it! Your bot is now running and ready to accept players.

## 📖 Usage

### Player Commands
- `/start` - Register and show main menu
- Create Room - Generate a new game room
- Join Room - Enter a room code to join
- My Stats - View your statistics
- Leaderboard - See top players
- Match History - Review past games

### Admin Commands
- `/admin` - Show admin panel
- `/stats` - View bot statistics
- `/listrooms` - List active rooms
- `/broadcast <message>` - Send message to all users
- `/addquestion` - Add new questions (feature in development)

## 🏗️ Project Structure

```
quiz_telegram_bot/
├── app/
│   ├── database/
│   │   ├── models.py              # SQLAlchemy models
│   │   ├── connection.py          # Database connection manager
│   │   └── repositories/          # Data access layer
│   ├── handlers/                  # Bot command handlers
│   │   ├── start.py              # Start command and main menu
│   │   ├── room.py               # Room creation/joining
│   │   ├── game.py               # Game logic handlers
│   │   ├── stats.py              # Statistics and leaderboard
│   │   └── admin.py              # Admin commands
│   ├── services/
│   │   ├── game_service.py       # Game business logic
│   │   └── redis_service.py      # Redis operations
│   ├── keyboards/
│   │   └── inline.py             # Telegram inline keyboards
│   ├── middleware/
│   │   └── database.py           # Database session middleware
│   ├── utils/
│   │   ├── logger.py             # Logging configuration
│   │   ├── room_code.py          # Room code generation
│   │   └── scoring.py            # Score calculation
│   ├── config.py                 # Application configuration
│   └── main.py                   # Application entry point
├── alembic/                      # Database migrations
├── scripts/
│   └── seed_questions.py         # Question seeding script
├── docker-compose.yml            # Docker orchestration
├── Dockerfile                    # Bot container definition
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🎯 How It Works

### Game Flow
1. **Room Creation**: Player 1 creates a room and gets a unique code
2. **Joining**: Player 2 joins using the room code
3. **Countdown**: 3-second countdown before game starts
4. **Questions**: 10 questions presented one at a time
5. **Answering**: Players have 15 seconds to answer each question
6. **Scoring**: Points awarded based on correctness and speed
7. **Results**: Final scores, winner, and statistics displayed
8. **Rating Update**: ELO ratings updated based on the outcome

### Scoring System
- **Base Score**: 100 points for correct answer
- **Time Bonus**: Up to 7.5 additional points for faster responses
- **Wrong Answer**: 0 points
- **No Answer**: 0 points

### ELO Rating
- Starting rating: 1000
- Win against higher-rated opponent: +32 to +50 points
- Win against lower-rated opponent: +10 to +25 points
- Loss: Inverse of win points (negative)
- Draw: No rating change

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BOT_TOKEN` | Telegram bot token | Required |
| `ADMIN_IDS` | Comma-separated admin user IDs | Empty |
| `DATABASE_URL` | PostgreSQL connection string | See .env.example |
| `REDIS_URL` | Redis connection string | redis://redis:6379/0 |
| `QUESTIONS_PER_GAME` | Number of questions per game | 10 |
| `QUESTION_TIME_LIMIT` | Seconds per question | 15 |
| `ROOM_CODE_LENGTH` | Length of room codes | 6 |
| `MAX_PLAYERS_PER_ROOM` | Maximum players per room | 2 |
| `ENVIRONMENT` | Environment (production/development) | production |
| `LOG_LEVEL` | Logging level | INFO |

## 🗄️ Database Schema

### Main Tables
- **users**: Player profiles and statistics
- **rooms**: Game room information
- **players**: Links users to rooms with game stats
- **questions**: Question pool with categories
- **answers**: Player answers with timing and correctness
- **match_history**: Completed game records
- **categories**: Question categories
- **friendships**: Friend connections (future feature)
- **daily_challenges**: Daily challenge data (future feature)

## 🐳 Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f bot

# Restart bot
docker-compose restart bot

# Run migrations
docker-compose exec bot alembic upgrade head

# Access PostgreSQL
docker-compose exec postgres psql -U quiz_user -d quiz_db

# Access Redis CLI
docker-compose exec redis redis-cli
```

## 🧪 Development

### Local Setup Without Docker

1. **Install Python 3.12+**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Use SQLite for development**
```env
DATABASE_URL=sqlite+aiosqlite:///./quiz_game.db
```

4. **Run migrations**
```bash
alembic upgrade head
```

5. **Seed questions**
```bash
python scripts/seed_questions.py
```

6. **Start bot**
```bash
python -m app.main
```

## 📝 Adding Questions

### Via Script
Edit `scripts/seed_questions.py` and add questions to the `QUESTIONS` list:

```python
{"category": "Science", "text": "What is the capital of France?", 
 "a": "London", "b": "Berlin", "c": "Paris", "d": "Madrid", 
 "correct": "C", "difficulty": "EASY"},
```

### Via Database
```sql
INSERT INTO questions (text, option_a, option_b, option_c, option_d, 
                       correct_answer, category_id, difficulty)
VALUES ('Your question?', 'Option A', 'Option B', 'Option C', 'Option D',
        'A', 1, 'medium');
```

## 🚀 Deployment

### Production Checklist
- [ ] Set strong database passwords
- [ ] Configure firewall rules
- [ ] Enable SSL for PostgreSQL
- [ ] Set up backup strategy
- [ ] Configure monitoring and alerts
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `LOG_LEVEL=WARNING` or `ERROR`
- [ ] Review admin access list

### Scaling
- Increase PostgreSQL connection pool size in `connection.py`
- Add Redis replication for high availability
- Run multiple bot instances with load balancing
- Use dedicated Redis for each service

## 🐛 Troubleshooting

### Bot not starting
```bash
# Check logs
docker-compose logs bot

# Verify environment variables
docker-compose config

# Ensure database is ready
docker-compose ps
```

### Database connection errors
```bash
# Check PostgreSQL status
docker-compose exec postgres pg_isready

# Verify credentials in .env
# Check network connectivity
```

### Redis connection errors
```bash
# Check Redis status
docker-compose exec redis redis-cli ping

# Should respond with PONG
```

## 📄 License

This project is provided as-is for educational purposes.

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review logs for error messages

---

Built with ❤️ using Python, aiogram, PostgreSQL, and Redis
