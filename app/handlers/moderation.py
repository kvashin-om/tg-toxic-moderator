"""Модерация: классифицируем и удаляем токсичное."""
import logging
import asyncio

from aiogram import Router, F
from aiogram.types import Message

from app.classifier import classifier

log = logging.getLogger(__name__)

router = Router(name="moderation")
router.message.filter(F.text)

DELETE_ENABLED = True


@router.message()
async def on_message(message: Message):
    text = message.text or ""
    user_id = message.from_user.id if message.from_user else None

    try:
        prob = await classifier.predict(text)
    except Exception:
        log.exception("Ошибка классификации, пропускаем")
        return

    is_toxic = prob >= classifier.cfg.threshold

    log.info(
        "MSG chat=%s user=%s prob=%.3f toxic=%s text=%r",
        message.chat.id, user_id, prob, is_toxic, text[:120],
    )

    if not is_toxic or not DELETE_ENABLED:
        return

    try:
        await message.delete()
        log.info("Удалено p=%.3f", prob)
    except Exception as e:
        log.warning("Не удалось удалить: %s", e)