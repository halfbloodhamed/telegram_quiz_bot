# Contributing to Telegram Quiz Game

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone <your-fork-url>`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Commit: `git commit -m "Add: your feature description"`
7. Push: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Development Setup

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Use SQLite for local testing
# Set in .env: DATABASE_URL=sqlite+aiosqlite:///./quiz_game.db

# Run migrations
alembic upgrade head

# Seed questions
python scripts/seed_questions.py

# Run bot
python -m app.main
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html
```

## Code Style

### Python Style Guide
- Follow PEP 8
- Use type hints for all functions
- Maximum line length: 100 characters
- Use descriptive variable names

### Example

```python
from typing import Optional, List

async def get_user_stats(
    user_id: int,
    include_history: bool = False
) -> Optional[Dict[str, Any]]:
    """
    Get user statistics.
    
    Args:
        user_id: The user's ID
        include_history: Whether to include match history
        
    Returns:
        Dictionary with user stats or None if user not found
    """
    # Implementation here
    pass
```

## Project Structure

- **app/** - Main application code
  - **handlers/** - Bot command handlers
  - **services/** - Business logic
  - **database/** - Database models and repositories
  - **keyboards/** - Telegram keyboards
  - **middleware/** - Bot middleware
  - **utils/** - Utility functions
  - **scheduler/** - Game flow management

- **scripts/** - Setup and maintenance scripts
- **tests/** - Test files
- **alembic/** - Database migrations

## Adding New Features

### Adding Questions

1. Edit `scripts/seed_questions.py`
2. Add questions to the `QUESTIONS` list
3. Run: `python scripts/seed_questions.py`

### Adding a New Category

1. Add category to `QUESTIONS` in seed script
2. Questions will auto-create categories

### Adding Bot Commands

1. Create handler in appropriate file in `app/handlers/`
2. Register router in `app/main.py`
3. Add command to documentation

### Adding Database Models

1. Add model to `app/database/models.py`
2. Create repository in `app/database/repositories/`
3. Generate migration: `alembic revision --autogenerate -m "Description"`
4. Review and edit migration if needed
5. Apply: `alembic upgrade head`

## Testing Guidelines

### Unit Tests
- Test individual functions
- Mock external dependencies
- Place in `tests/test_*.py`

### Integration Tests
- Test feature flows
- Use test database
- Clean up after tests

### Example Test

```python
import pytest
from app.utils.scoring import calculate_score

def test_calculate_score_correct():
    """Test score calculation for correct answer"""
    score = calculate_score(True, 5.0)
    assert score > 100
    
def test_calculate_score_incorrect():
    """Test score calculation for incorrect answer"""
    score = calculate_score(False, 5.0)
    assert score == 0
```

## Pull Request Guidelines

### PR Title Format
- `Add: <description>` - New feature
- `Fix: <description>` - Bug fix
- `Update: <description>` - Updates to existing feature
- `Docs: <description>` - Documentation changes
- `Refactor: <description>` - Code refactoring

### PR Description Should Include
1. What changed
2. Why it changed
3. How to test it
4. Screenshots (if UI changes)
5. Breaking changes (if any)

### Before Submitting
- [ ] Code follows project style
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No console errors or warnings
- [ ] Tested locally

## Common Tasks

### Adding a New Keyboard

```python
# In app/keyboards/inline.py

def get_my_keyboard() -> InlineKeyboardMarkup:
    """Description of keyboard"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Button", callback_data="action")],
    ])
```

### Adding a New Service Method

```python
# In app/services/game_service.py

async def my_new_method(self, param: str) -> Optional[Model]:
    """
    Method description.
    
    Args:
        param: Parameter description
        
    Returns:
        Result description
    """
    # Implementation
    pass
```

### Adding a New Repository Method

```python
# In app/database/repositories/user_repository.py

async def get_users_by_rating(
    self,
    min_rating: int,
    limit: int = 10
) -> List[User]:
    """Get users above minimum rating"""
    result = await self.session.execute(
        select(User)
        .where(User.rating >= min_rating)
        .order_by(desc(User.rating))
        .limit(limit)
    )
    return list(result.scalars().all())
```

## Reporting Issues

### Bug Reports Should Include
1. Description of the bug
2. Steps to reproduce
3. Expected behavior
4. Actual behavior
5. Environment (OS, Python version, Docker version)
6. Logs (if applicable)

### Feature Requests Should Include
1. Clear description of feature
2. Use case / why it's needed
3. Proposed implementation (optional)
4. Examples from similar projects (optional)

## Code Review Process

1. Maintainer reviews PR
2. Feedback provided if needed
3. Changes requested or approved
4. PR merged into main branch

## Questions?

- Open an issue for questions
- Check existing issues first
- Be respectful and constructive

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing! 🎉
