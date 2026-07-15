# 🚀 Quick Start Guide

## Prerequisites
- Docker Desktop installed
- Telegram Bot Token from [@BotFather](https://t.me/botfather)

## 5-Minute Setup

### Step 1: Get Your Bot Token
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the bot token (looks like: `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`)

### Step 2: Get Your Admin ID
1. Search for `@userinfobot` in Telegram
2. Start the bot
3. Copy your user ID (a number like `123456789`)

### Step 3: Clone and Configure
```bash
# Clone repository
git clone <repository-url>
cd quiz_telegram_bot

# Create .env file
copy .env.example .env

# Edit .env and add your credentials:
# BOT_TOKEN=your_bot_token_here
# ADMIN_IDS=your_user_id_here
```

### Step 4: Start Everything
```bash
# Start all services (PostgreSQL, Redis, Bot)
docker-compose up -d

# Wait 10 seconds for database to be ready
# Then seed questions
docker-compose exec bot python scripts/seed_questions.py

# Check if bot is running
docker-compose logs -f bot
```

### Step 5: Test Your Bot
1. Open Telegram
2. Search for your bot by username
3. Send `/start`
4. Click "Create Room"
5. Share the room code with a friend!

## Common Issues

### "connection refused" error
Wait 30 seconds for PostgreSQL to start, then restart the bot:
```bash
docker-compose restart bot
```

### Bot doesn't respond
Check logs:
```bash
docker-compose logs bot
```

Verify bot token in .env file is correct.

### Questions not loading
Run seed script:
```bash
docker-compose exec bot python scripts/seed_questions.py
```

## Next Steps

- Add more questions to `scripts/seed_questions.py`
- Invite friends to play
- Check leaderboard to see rankings
- View match history to track progress

## Stop the Bot

```bash
docker-compose down
```

## Update the Bot

```bash
git pull
docker-compose up -d --build
```

---

**Need Help?** Check README.md for detailed documentation.
