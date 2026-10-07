"""Команды: /start, /ping."""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="common")


@router.message(Command("start"))
async def on_start(message: Message):
    await message.answer("Привет! Я чищу токсичные сообщения.")


@router.message(Command("ping"))
async def on_ping(message: Message):
    await message.answer("pong")