import logging

from aiogram import Bot, Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

import config as cfg

bot = Bot(token=cfg.INVITE_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


async def get_invite_link(chat_id, member_limit):
    try:
        link = await bot.create_chat_invite_link(chat_id=int(chat_id), member_limit=int(member_limit))
        return link.invite_link
    except:
        link = await bot.create_chat_invite_link(chat_id=int(chat_id), member_limit=int(member_limit))
        return link["invite_link"]


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False, on_shutdown=shutdown)