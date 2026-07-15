# Deployment Guide

This guide covers deploying the Telegram Quiz Game Bot to various environments.

## Table of Contents
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Cloud Platforms](#cloud-platforms)
- [Monitoring](#monitoring)
- [Backup and Recovery](#backup-and-recovery)

## Local Development

### Prerequisites
- Python 3.12+
- PostgreSQL 16+ (or use SQLite)
- Redis 7+
- Telegram Bot Token

### Setup

1. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

For local development, use SQLite:
```env
DATABASE_URL=sqlite+aiosqlite:///./quiz_game.db
```

3. **Run migrations**
```bash
alembic upgrade head
```

4. **Seed questions**
```bash
python scripts/seed_questions.py
```

5. **Start bot**
```bash
python -m app.main
```

## Docker Deployment

### Quick Start

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f bot

# Stop services
docker-compose down
```

### Custom Configuration

Create `docker-compose.override.yml` for custom settings:

```yaml
version: '3.8'

services:
  bot:
    environment:
      - LOG_LEVEL=DEBUG
    restart: always
  
  postgres:
    ports:
      - "5433:5432"  # Different external port
```

### Building Custom Image

```bash
# Build image
docker build -t quiz-bot:latest .

# Run container
docker run -d \
  --name quiz-bot \
  --env-file .env \
  --network host \
  quiz-bot:latest
```

## Production Deployment

### Security Checklist

- [ ] Use strong database passwords
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `LOG_LEVEL=WARNING` or `ERROR`
- [ ] Enable PostgreSQL SSL
- [ ] Configure firewall rules
- [ ] Restrict admin access
- [ ] Use secrets management
- [ ] Enable Redis authentication
- [ ] Regular security updates

### Environment Variables

Production `.env`:
```env
BOT_TOKEN=your_production_bot_token
ADMIN_IDS=123456789,987654321

DATABASE_URL=postgresql+asyncpg://user:strong_password@postgres:5432/quiz_db
REDIS_URL=redis://:redis_password@redis:6379/0

ENVIRONMENT=production
LOG_LEVEL=WARNING

QUESTIONS_PER_GAME=10
QUESTION_TIME_LIMIT=15
```

### Database Setup

1. **Create database**
```sql
CREATE DATABASE quiz_db;
CREATE USER quiz_user WITH ENCRYPTED PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE quiz_db TO quiz_user;
```

2. **Run migrations**
```bash
alembic upgrade head
```

3. **Seed data**
```bash
python scripts/seed_questions.py
```

### Docker Compose for Production

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    restart: always
    environment:
      POSTGRES_USER: quiz_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: quiz_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    command: >
      postgres
      -c ssl=on
      -c ssl_cert_file=/etc/ssl/certs/server.crt
      -c ssl_key_file=/etc/ssl/private/server.key

  redis:
    image: redis:7-alpine
    restart: always
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data

  bot:
    build: .
    restart: always
    depends_on:
      - postgres
      - redis
    env_file:
      - .env
    healthcheck:
      test: ["CMD-SHELL", "pgrep -f 'python -m app.main'"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
  redis_data:
```

## Cloud Platforms

### AWS Deployment

#### Using EC2

1. **Launch EC2 instance**
   - Ubuntu 22.04 LTS
   - t3.small or larger
   - Security group: SSH (22), PostgreSQL (5432), Redis (6379)

2. **Install Docker**
```bash
sudo apt update
sudo apt install docker.io docker-compose -y
sudo systemctl enable docker
```

3. **Deploy application**
```bash
git clone <repository>
cd quiz_telegram_bot
cp .env.example .env
# Edit .env
docker-compose up -d
```

#### Using ECS (Elastic Container Service)

1. Create ECR repository
2. Push Docker image
3. Create ECS task definition
4. Deploy to ECS cluster
5. Use RDS for PostgreSQL
6. Use ElastiCache for Redis

### Google Cloud Platform

#### Using Compute Engine

Similar to AWS EC2 deployment.

#### Using Cloud Run

1. Build and push to Container Registry
2. Deploy to Cloud Run
3. Use Cloud SQL for PostgreSQL
4. Use Memorystore for Redis

### Heroku

1. **Create Heroku app**
```bash
heroku create quiz-telegram-bot
```

2. **Add PostgreSQL**
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

3. **Add Redis**
```bash
heroku addons:create heroku-redis:hobby-dev
```

4. **Set config**
```bash
heroku config:set BOT_TOKEN=your_bot_token
heroku config:set ADMIN_IDS=your_telegram_id
```

5. **Deploy**
```bash
git push heroku main
```

### DigitalOcean

#### Using Droplet

1. Create Ubuntu Droplet (2GB RAM minimum)
2. Install Docker and Docker Compose
3. Clone repository
4. Configure `.env`
5. Run `docker-compose up -d`

#### Using App Platform

1. Create app from GitHub
2. Add PostgreSQL database
3. Add Redis database
4. Set environment variables
5. Deploy

## Monitoring

### Logging

**View logs:**
```bash
docker-compose logs -f bot
```

**Save logs to file:**
```bash
docker-compose logs bot > bot.log
```

**Structured logging:**
Logs are in format: `TIMESTAMP - LOGGER - LEVEL - MESSAGE`

### Health Checks

**Manual check:**
```bash
docker-compose ps
```

**Automated monitoring:**
- Use health check endpoints
- Monitor container status
- Set up alerts

### Metrics

Track these metrics:
- Active games
- Total users
- Questions answered per day
- Average response time
- Error rate
- Database connection pool usage

### Alerting

Set up alerts for:
- Bot down
- Database connection failures
- High error rate
- Memory/CPU usage
- Disk space

## Backup and Recovery

### Database Backup

**Manual backup:**
```bash
docker-compose exec postgres pg_dump -U quiz_user quiz_db > backup.sql
```

**Automated backup script:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U quiz_user quiz_db > backup_$DATE.sql
# Upload to S3 or other storage
```

**Schedule with cron:**
```bash
0 2 * * * /path/to/backup.sh
```

### Database Restore

```bash
# Stop bot
docker-compose stop bot

# Restore database
cat backup.sql | docker-compose exec -T postgres psql -U quiz_user quiz_db

# Start bot
docker-compose start bot
```

### Redis Backup

Redis automatically saves to disk. To backup:
```bash
docker-compose exec redis redis-cli SAVE
docker cp quiz_redis:/data/dump.rdb ./redis_backup.rdb
```

## Scaling

### Vertical Scaling

Increase resources for containers:
```yaml
services:
  bot:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

### Horizontal Scaling

Run multiple bot instances:
```yaml
services:
  bot:
    deploy:
      replicas: 3
```

**Note:** Ensure proper session management for multiple instances.

### Database Scaling

- Enable connection pooling (already configured)
- Add read replicas
- Optimize queries
- Add indexes

### Redis Scaling

- Add Redis Sentinel for high availability
- Use Redis Cluster for sharding
- Add replication

## SSL/TLS

### PostgreSQL SSL

1. Generate certificates
2. Mount certificates in container
3. Update connection string:
```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db?ssl=require
```

### Redis TLS

```yaml
services:
  redis:
    command: >
      redis-server
      --tls-port 6379
      --port 0
      --tls-cert-file /certs/redis.crt
      --tls-key-file /certs/redis.key
```

## Troubleshooting

### Bot Won't Start

1. Check logs: `docker-compose logs bot`
2. Verify bot token in `.env`
3. Ensure database is ready
4. Check network connectivity

### Database Connection Errors

1. Verify PostgreSQL is running
2. Check connection string
3. Test connection: `docker-compose exec postgres psql -U quiz_user quiz_db`
4. Check firewall rules

### Memory Issues

1. Monitor usage: `docker stats`
2. Increase limits in docker-compose.yml
3. Check for memory leaks
4. Restart services: `docker-compose restart`

### High CPU Usage

1. Check concurrent games
2. Optimize database queries
3. Add indexes
4. Scale horizontally

## Maintenance

### Regular Tasks

**Daily:**
- Check logs for errors
- Monitor active games
- Verify backups

**Weekly:**
- Review user growth
- Check database size
- Clean up old data

**Monthly:**
- Update dependencies
- Review security
- Optimize database
- Update documentation

### Updates

**Update bot code:**
```bash
git pull
docker-compose up -d --build
```

**Update dependencies:**
```bash
pip install -r requirements.txt --upgrade
docker-compose up -d --build
```

**Run new migrations:**
```bash
docker-compose exec bot alembic upgrade head
```

## Performance Optimization

### Database

- Add indexes on frequently queried columns
- Use connection pooling (configured)
- Vacuum regularly
- Analyze query plans

### Redis

- Set appropriate TTLs
- Use pipelines for bulk operations
- Monitor memory usage
- Configure maxmemory policies

### Application

- Use async/await throughout (done)
- Minimize database queries
- Cache frequently accessed data
- Use Redis for temporary state

## Support

For issues:
1. Check logs
2. Review documentation
3. Search existing issues
4. Open new issue with details

---

**Security Note:** Never commit `.env` files or credentials to version control.

**Best Practice:** Use secrets management services (AWS Secrets Manager, HashiCorp Vault, etc.) for production.
