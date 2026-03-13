"""
main.py — точка входа

Запуск:
  python main.py

Переменные окружения (задаются в панели bothost.ru):
  API_TOKEN        — токен от @BotFather
  LEADS_CHANNEL_ID — ID приватного канала для получения заявок
"""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers.common import start as common_start
from handlers.user import flow as user_flow

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def main() -> None:
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher(storage=MemoryStorage())

    # Регистрируем роутеры
    dp.include_router(common_start.router)
    dp.include_router(user_flow.router)

    logger.info("⚖️ Debt Bot запущен!")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
