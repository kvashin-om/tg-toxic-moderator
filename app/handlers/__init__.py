"""Пакет хендлеров. Здесь собираем все роутеры в один."""

from aiogram import Router

from .common import router as common_router
# from .messages import router as messages_router
from .moderation import router as moderation_router

# Главный роутер пакета. Подключаем к нему дочерние.
router = Router(name="handlers")
router.include_router(common_router)
# router.include_router(messages_router)
router.include_router(moderation_router)
