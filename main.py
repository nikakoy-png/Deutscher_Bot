import asyncio
from aiogram.filters import Command
from telebot import *
from BotController import dp, bot, router, rating


async def main() -> None:
    dp.include_router(router=router)
    dp.message.register(rating, Command(commands="rating"))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
