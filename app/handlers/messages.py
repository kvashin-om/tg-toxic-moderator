"""Обработка обычных текстовых сообщений."""
from aiogram import Router, F
from aiogram.types import Message

router = Router(name="messages")


@router.message(F.text)
async def on_text(message: Message):
    await message.answer("I'm sorry, I didn't understand that command.")