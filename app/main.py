import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

from aiogram import Bot, Dispatcher

from app.config import settings
from app.handlers import router

log = logging.getLogger(__name__)


async def main() -> None:
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    dp.include_router(router)

    try:
        # 1. Сбрасываем все накопившиеся старые сообщения на сервере Telegram
        await bot.delete_webhook(drop_pending_updates=True)
        
        # 2. Запускаем опрос
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Остановлен")
