from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import database as db
import keyboards as kb
import pytz

kyiv = pytz.timezone("Europe/Kiev")
scheduler = AsyncIOScheduler(timezone="Europe/Kiev")

async def send_afternoon_reminders(bot):
    cursor = db.get_cursor()
    now = datetime.now(kyiv)
    tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT bookings.id, users.tg_id,
               bookings.service, bookings.master,
               bookings.date, bookings.time
        FROM bookings
        JOIN users ON bookings.user_id = users.id
        WHERE bookings.date = %s
        AND users.tg_id != 0
        AND bookings.reminded_afternoon = 0
    """, (tomorrow,))

    bookings = cursor.fetchall()

    for b in bookings:
        booking_id, tg_id, service, master, date, time = b
        try:
            await bot.send_message(
                tg_id,
                f"🌸 *Нагадування про завтрашній запис!*\n\n"
                f"Чекаємо вас завтра о *{time}* 💖\n\n"
                f"🔍 {service}\n"
                f"👩‍🎨 {master}\n\n"
                f"Якщо плани змінились — скасуйте запис заздалегідь 🙏",
                parse_mode="Markdown"
            )
            cursor.execute(
                "UPDATE bookings SET reminded_afternoon = 1 WHERE id = %s",
                (booking_id,)
            )
            db.conn.commit()
        except Exception as e:
            print(f"❌ Помилка: {e}")


async def send_hour_before_reminders(bot):
    cursor = db.get_cursor()
    now = datetime.now(kyiv)
    today = now.strftime("%Y-%m-%d")
    time_from = (now + timedelta(minutes=50)).strftime("%H:%M")
    time_to = (now + timedelta(minutes=75)).strftime("%H:%M")

    cursor.execute("""
        SELECT bookings.id, users.tg_id,
               bookings.service, bookings.master,
               bookings.date, bookings.time
        FROM bookings
        JOIN users ON bookings.user_id = users.id
        WHERE bookings.date = %s
        AND bookings.time BETWEEN %s AND %s
        AND users.tg_id != 0
        AND bookings.reminded_before = 0
    """, (today, time_from, time_to))

    bookings = cursor.fetchall()

    for b in bookings:
        booking_id, tg_id, service, master, date, time = b
        try:
            await bot.send_message(
                tg_id,
                f"⏰ *Вже скоро ваш запис!*\n\n"
                f"О *{time}* чекаємо на вас 💖\n\n"
                f"🔍 {service}\n"
                f"👩‍🎨 {master}",
                parse_mode="Markdown"
            )
            cursor.execute(
                "UPDATE bookings SET reminded_before = 1 WHERE id = %s",
                (booking_id,)
            )
            db.conn.commit()
        except Exception as e:
            print(f"❌ Помилка: {e}")


async def send_review_requests(bot):
    cursor = db.get_cursor()
    now = datetime.now(kyiv)
    today = now.strftime("%Y-%m-%d")
    time_from = (now - timedelta(minutes=150)).strftime("%H:%M")
    time_to = (now - timedelta(minutes=120)).strftime("%H:%M")

    cursor.execute("""
        SELECT bookings.id, users.tg_id,
               bookings.service, bookings.master,
               bookings.date, bookings.time
        FROM bookings
        JOIN users ON bookings.user_id = users.id
        WHERE bookings.date = %s
        AND bookings.time BETWEEN %s AND %s
        AND users.tg_id != 0
        AND bookings.reviewed = 0
    """, (today, time_from, time_to))

    bookings = cursor.fetchall()

    for b in bookings:
        booking_id, tg_id, service, master, date, time = b
        try:
            await bot.send_message(
                tg_id,
                f"💖 Дякуємо за візит!\n\n"
                f"🔍 {service}\n"
                f"👩‍🎨 {master}\n\n"
                f"Будемо вдячні якщо оціните якість обслуговування 👇",
                reply_markup=kb.rating_kb
            )
            cursor.execute(
                "UPDATE bookings SET reviewed = 1 WHERE id = %s",
                (booking_id,)
            )
            db.conn.commit()
        except Exception as e:
            print(f"❌ Помилка: {e}")