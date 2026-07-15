import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.config import settings
from app.database.connection import db_manager
from app.database.models import Base
from app.database.repositories.question_repository import QuestionRepository, CategoryRepository
from app.database.models import DifficultyLevel
from app.services.redis_service import redis_service
from app.handlers import start, room, game, stats, admin
from app.middleware.database import DatabaseMiddleware
from app.scheduler.game_scheduler import GameScheduler, set_game_scheduler
from app.utils.logger import logger


async def on_startup(bot: Bot):
    """Actions on startup"""
    logger.info("Bot is starting...")

    # Ensure database schema exists before handling updates
    async with db_manager.engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    # Seed default questions if the database is empty
    async with db_manager.async_session() as session:
        question_repo = QuestionRepository(session)
        category_repo = CategoryRepository(session)

        total_questions = await question_repo.get_total_questions()
        if total_questions == 0:
            default_questions = [
                ("Programming", "What does HTML stand for?", "Hyper Text Markup Language", "High Tech Modern Language", "Home Tool Markup Language", "Hyperlinks and Text Markup Language", "A", DifficultyLevel.EASY),
                ("Programming", "Which programming language is known as the 'language of the web'?", "Python", "JavaScript", "Java", "C++", "B", DifficultyLevel.EASY),
                ("Programming", "What is the time complexity of binary search?", "O(n)", "O(log n)", "O(n²)", "O(1)", "B", DifficultyLevel.MEDIUM),
                ("Programming", "Which data structure uses LIFO?", "Queue", "Array", "Stack", "Tree", "C", DifficultyLevel.EASY),
                ("Programming", "What does SQL stand for?", "Structured Query Language", "Simple Question Language", "Structured Question Language", "Simple Query Language", "A", DifficultyLevel.EASY),
                ("Science", "What is the chemical symbol for gold?", "Go", "Gd", "Au", "Ag", "C", DifficultyLevel.MEDIUM),
                ("Science", "How many planets are in our solar system?", "7", "8", "9", "10", "B", DifficultyLevel.EASY),
                ("Science", "What is the speed of light?", "300,000 km/s", "150,000 km/s", "500,000 km/s", "200,000 km/s", "A", DifficultyLevel.MEDIUM),
                ("Science", "What is H2O?", "Oxygen", "Hydrogen", "Water", "Carbon Dioxide", "C", DifficultyLevel.EASY),
                ("Science", "Who developed the theory of relativity?", "Isaac Newton", "Albert Einstein", "Stephen Hawking", "Nikola Tesla", "B", DifficultyLevel.MEDIUM),
                ("History", "In which year did World War II end?", "1943", "1944", "1945", "1946", "C", DifficultyLevel.MEDIUM),
                ("History", "Who was the first President of the United States?", "Thomas Jefferson", "George Washington", "John Adams", "Benjamin Franklin", "B", DifficultyLevel.EASY),
                ("History", "When did the Berlin Wall fall?", "1987", "1988", "1989", "1990", "C", DifficultyLevel.MEDIUM),
                ("History", "Which ancient wonder is still standing?", "Hanging Gardens of Babylon", "Colossus of Rhodes", "Great Pyramid of Giza", "Lighthouse of Alexandria", "C", DifficultyLevel.MEDIUM),
                ("History", "Who painted the Mona Lisa?", "Vincent van Gogh", "Pablo Picasso", "Leonardo da Vinci", "Michelangelo", "C", DifficultyLevel.EASY),
                ("Sports", "How many players are on a soccer team?", "9", "10", "11", "12", "C", DifficultyLevel.EASY),
                ("Sports", "Which country won the 2018 FIFA World Cup?", "Brazil", "Germany", "France", "Argentina", "C", DifficultyLevel.MEDIUM),
                ("Sports", "What is the diameter of a basketball hoop?", "16 inches", "18 inches", "20 inches", "22 inches", "B", DifficultyLevel.HARD),
                ("Movies", "Who directed Titanic?", "Steven Spielberg", "James Cameron", "Christopher Nolan", "Martin Scorsese", "B", DifficultyLevel.MEDIUM),
                ("Movies", "Which movie won the first Academy Award for Best Picture?", "Wings", "Sunrise", "The Jazz Singer", "7th Heaven", "A", DifficultyLevel.HARD),
            ]

            categories = {}
            for category_name in ["Programming", "Science", "History", "Sports", "Movies"]:
                category = await category_repo.get_by_name(category_name)
                if not category:
                    category = await category_repo.create(category_name)
                categories[category_name] = category.id

            for category_name, text, option_a, option_b, option_c, option_d, correct_answer, difficulty in default_questions:
                category_id = categories.get(category_name)
                await question_repo.create(
                    text=text,
                    option_a=option_a,
                    option_b=option_b,
                    option_c=option_c,
                    option_d=option_d,
                    correct_answer=correct_answer,
                    category_id=category_id,
                    difficulty=difficulty,
                )

            await session.commit()
            logger.info("Seeded default quiz questions")

    await redis_service.connect()
    
    # Initialize game scheduler
    scheduler = GameScheduler(bot)
    set_game_scheduler(scheduler)
    
    logger.info("Bot started successfully")


async def on_shutdown(bot: Bot):
    """Actions on shutdown"""
    logger.info("Bot is shutting down...")
    await redis_service.disconnect()
    await db_manager.close()
    logger.info("Bot stopped")


async def main():
    """Main function"""
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
    )
    
    dp = Dispatcher()
    
    # Register middleware
    dp.update.middleware(DatabaseMiddleware())
    
    # Register handlers
    dp.include_router(start.router)
    dp.include_router(room.router)
    dp.include_router(game.router)
    dp.include_router(stats.router)
    dp.include_router(admin.router)
    
    # Register startup/shutdown handlers
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Start bot
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped by user")
