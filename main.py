import asyncio
from aiogram import Bot, Dispatcher
from handlers import user
import os
from dotenv import load_dotenv
load_dotenv()
from scheduler import scheduler, send_afternoon_reminders, send_hour_before_reminders, send_review_requests

async def main():

    TOKEN = os.getenv("BOT_TOKEN")

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    dp.include_router(user)
    scheduler.add_job(
        send_afternoon_reminders,
        "cron",
        hour=14,
        minute=0,
        args=[bot]
    )

    scheduler.add_job(
        send_hour_before_reminders,
        "interval",
        minutes=15,
        args=[bot]
    )

    scheduler.add_job(
        send_review_requests,
        "interval",
        minutes=15,
        args=[bot]
    )

    scheduler.start()
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
