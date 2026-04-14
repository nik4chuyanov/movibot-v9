from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.bot_handlers import register_handlers
from app.config import Settings
from app.services import ServiceContainer

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


async def run_polling() -> None:
    settings = Settings.from_env()
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required to run the bot")

    services = ServiceContainer(settings)
    await services.connect()

    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dispatcher = Dispatcher()
    register_handlers(dispatcher, services, settings.admin_ids)

    LOGGER.info("Starting Telegram polling")
    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()
        await services.close()


if __name__ == "__main__":
    asyncio.run(run_polling())
