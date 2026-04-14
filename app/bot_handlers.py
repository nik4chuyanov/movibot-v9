from __future__ import annotations

from aiogram import Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message

from app.services import ServiceContainer


def register_handlers(dispatcher: Dispatcher, services: ServiceContainer, admin_ids: set[int]) -> None:
    @dispatcher.message(Command("start"))
    async def start_handler(message: Message) -> None:
        user = message.from_user
        user_id = user.id if user else 0
        if services.redis is not None:
            await services.redis.incr(f"users:{user_id}:starts")

        await message.answer(
            "👋 Hello! Movibot is online. Use /help for commands."
        )

    @dispatcher.message(Command("help"))
    async def help_handler(message: Message) -> None:
        await message.answer(
            "Commands:\n"
            "/start - Start the bot\n"
            "/admin_ping - Admin-only connectivity check\n"
            "/admin_jobs - Admin-only scheduler info"
        )

    @dispatcher.message(Command("admin_ping"), F.from_user.id.in_(admin_ids))
    async def admin_ping_handler(message: Message) -> None:
        status = await services.ping()
        await message.answer(f"✅ Admin ping: postgres={status['postgres']}, redis={status['redis']}")

    @dispatcher.message(Command("admin_jobs"), F.from_user.id.in_(admin_ids))
    async def admin_jobs_handler(message: Message) -> None:
        await message.answer(
            "Scheduler runs in API service. Heartbeat job interval is controlled by "
            "SCHEDULER_INTERVAL_SECONDS."
        )

    @dispatcher.message(Command("admin_ping", "admin_jobs"))
    async def admin_denied_handler(message: Message) -> None:
        await message.answer("⛔ This command is available only for admins.")
