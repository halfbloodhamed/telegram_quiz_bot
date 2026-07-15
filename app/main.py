import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.config import settings
from app.database.connection import db_manager
from app.services.redis_service import redis_service
from app.handlers import start, room, game, stats, admin
from app.middleware.database import DatabaseMiddleware
from app.scheduler.game_scheduler import GameScheduler, set_game_scheduler
from app.utils.logger import logger


async def on_startup(bot: Bot):
    """Actions on startup"""
    logger.info("Bot is starting...")
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
