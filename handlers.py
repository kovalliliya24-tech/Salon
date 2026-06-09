from aiogram import F, Router
import keyboards as kb
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters.command import CommandStart
from aiogram.types import FSInputFile
from keyboards import reviews_kb
reply_markup=reviews_kb
from states import Registration
from states import Booking
from aiogram.filters import Command
from database import cursor, conn
from datetime import datetime, timedelta
from states import AdminAction, Review, AdminBooking
import os


user = Router()



@user.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):

    await state.clear()

    cursor.execute(
        "SELECT * FROM users WHERE tg_id = %s",
        (message.from_user.id,)
    )
    existing_user = cursor.fetchone()

    if existing_user:
        await message.answer(
            "🫶 З поверненням! Оберіть опцію 👇",
            reply_markup=kb.menu_front
        )
        return

    await message.answer(
        "👋 Привіт! Будь ласка, введіть ваше ім’я:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Registration.name)

@user.message(Registration.name)
async def reg_name(message: Message, state: FSMContext):

    if message.text.startswith("/"):
        await message.answer("❌ Введіть, будь ласка, ім’я, а не команду")
        return

    await state.update_data(name=message.text)

    await message.answer(
        '📞 Надішліть номер телефону використовуючи кнопку нижче👇',
        reply_markup=kb.get_number
    )
    await state.set_state(Registration.phone)

@user.message(Registration.phone, F.contact)
async def reg_contact(message: Message, state: FSMContext):
    phone = message.contact.phone_number.replace(" ", "")
    if not phone.startswith("+"):
        phone = "+" + phone

    data = await state.get_data()

    cursor.execute(
        "SELECT * FROM users WHERE tg_id = %s",
        (message.from_user.id,)
    )
    existing_user = cursor.fetchone()

    if not existing_user:
        cursor.execute(
            "INSERT INTO users (tg_id, name, phone) VALUES (%s, %s, %s)",
            (message.from_user.id, data["name"], phone)
        )
        conn.commit()

    await message.answer(
        f'✅ Дякуємо!\nВи успішно зареєстровані 🎉\n\n'
        f'Ім`я: {data["name"]}\nНомер телефону: {phone}',
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer("🫶 Виберіть опцію з меню:", reply_markup=kb.menu_front)
    await state.clear()

@user.message(Registration.phone)
async def reg_contact(message: Message, state: FSMContext):
    await message.answer('Надішліть контакт використовуючи кнопку нижче👇!')

services_dict = {
    "service_1": " Ваша послуга",
    "service_2": " Ваша послуга",
    "service_3": " Ваша послуга"
}

masters_dict = {
    "master_1": " Ваш майстер",
    "master_2": " Ваш майстер",
    "master_3": " Ваш майстер"
}

# ADMIN_ID = 6484982821
ADMIN_IDS = [
    int(x.strip())
    for x in os.getenv("ADMIN_IDS", "").split(",")
    if x.strip()
]

def is_admin(user_id: int):
    return user_id in ADMIN_IDS

@user.message(Command("admin"))
async def admin_panel(message: Message):

    if not is_admin(message.from_user.id):
        await message.answer("❌ Немає доступу")
        return

    await message.answer(
        "🔐 Адмін панель",
        reply_markup=kb.admin_kb
    )

@user.callback_query(lambda c: c.data == "admin_add")
async def admin_add_callback(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Немає доступу", show_alert=True)
        return

    await state.set_state(AdminBooking.client_name)
    await callback.message.answer("👤 Введіть ім'я клієнта:")
    await callback.answer()


@user.message(AdminBooking.client_name)
async def admin_booking_name(message: Message, state: FSMContext):
    name = message.text.strip()

    if not name or name.startswith("/"):
        await message.answer("❌ Введіть коректне ім'я клієнта:")
        return

    if any(char.isdigit() for char in name):
        await message.answer("❌ Ім'я не може містити цифри. Введіть ім'я клієнта:")
        return

    await state.update_data(client_name=name)
    await state.set_state(AdminBooking.client_phone)
    await message.answer("📞 Введіть телефон клієнта:\n\nПриклад: +380991112233")


@user.message(AdminBooking.client_phone)
async def admin_booking_phone(message: Message, state: FSMContext):
    phone = message.text.strip()

    phone = phone.replace(" ", "").replace("-", "")

    if not phone.startswith("+"):
        phone = "+" + phone

    if not phone[1:].isdigit():
        await message.answer(
            "❌ Невірний формат телефону\n\n"
            "Введіть номер у форматі: +380991112233"
        )
        return

    if len(phone) < 10 or len(phone) > 15:
        await message.answer(
            "❌ Номер телефону занадто короткий або довгий\n\n"
            "Введіть номер у форматі: +380991112233"
        )
        return

    await state.update_data(client_phone=phone)
    await state.set_state(AdminBooking.service)
    await message.answer("🔍 Оберіть послугу 👇", reply_markup=kb.services_kb)


@user.callback_query(AdminBooking.service, lambda c: c.data.startswith("service_"))
async def admin_booking_service(callback: CallbackQuery, state: FSMContext):
    await state.update_data(service=callback.data)
    await state.set_state(AdminBooking.master)
    await callback.message.answer("👩‍🎨 Оберіть майстра 👇", reply_markup=kb.masters_kb)
    await callback.answer()

@user.callback_query(AdminBooking.master, lambda c: c.data.startswith("master_"))
async def admin_booking_master(callback: CallbackQuery, state: FSMContext):
    await state.update_data(master=callback.data)
    await state.set_state(AdminBooking.date)
    await callback.message.answer("📅 Оберіть дату 👇", reply_markup=kb.get_dates_kb(get_dates()))
    await callback.answer()

@user.callback_query(AdminBooking.date, lambda c: c.data.startswith("date_"))
async def admin_booking_date(callback: CallbackQuery, state: FSMContext):
    date_key = callback.data
    data = await state.get_data()

    free_times = get_free_times(data["master"], date_key)

    if not free_times:
        await callback.answer("❌ Немає вільного часу, оберіть іншу дату", show_alert=True)
        return

    await state.update_data(date=date_key)
    await state.set_state(AdminBooking.time)
    await callback.message.answer("🕐 Оберіть час 👇", reply_markup=kb.get_times_kb(free_times))
    await callback.answer()

@user.callback_query(AdminBooking.time, lambda c: c.data.startswith("time_"))
async def admin_booking_time(callback: CallbackQuery, state: FSMContext):
    time_key = callback.data
    data = await state.get_data()

    date_key = data["date"]
    time_text = get_times(date_key)[time_key]
    date_text = get_dates()[date_key]

    await state.update_data(time=time_key)

    await callback.message.answer(
        f"📋 *Підтвердіть запис:*\n\n"
        f"👤 {data['client_name']} ({data['client_phone']})\n"
        f"🔍 {services_dict[data['service']]}\n"
        f"👩‍🎨 {masters_dict[data['master']]}\n"
        f"📅 {date_text}\n"
        f"🕐 {time_text}\n\n"
        f"Все правильно? 👇",
        parse_mode="Markdown",
        reply_markup=kb.admin_confirm_yes_kb()
    )
    await callback.answer()


@user.callback_query(lambda c: c.data == "admin_confirm_yes")
async def admin_confirm_yes(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    date_key = data["date"]
    time_key = data["time"]
    time_text = get_times(date_key)[time_key]
    date_text = get_dates()[date_key]
    real_date = (datetime.now() + timedelta(days=int(date_key.split("_")[1]))).strftime("%Y-%m-%d")

    cursor.execute(
        "SELECT id FROM users WHERE phone=%s AND name=%s",
        (data["client_phone"], data["client_name"])
    )
    user_row = cursor.fetchone()

    if user_row:
        user_id = user_row[0]
    else:
        cursor.execute(
            "INSERT INTO users (tg_id, name, phone) VALUES (%s, %s, %s)",
            (0, data["client_name"], data["client_phone"])
        )
        conn.commit()
        user_id = cursor.fetchone()[0]

    cursor.execute("""
        SELECT * FROM bookings 
        WHERE master=%s AND date=%s AND time=%s
    """, (data["master"], real_date, time_text))

    if cursor.fetchone():
        await callback.message.answer(
            "❌ Хтось щойно зайняв цей час. Оберіть інший 👇",
            reply_markup=kb.admin_kb
        )
        await state.clear()
        await callback.answer()
        return

    cursor.execute(
        "INSERT INTO bookings (user_id, service, master, date, time) VALUES (%s, %s, %s, %s, %s)",
        (user_id, data["service"], data["master"], real_date, time_text)
    )
    conn.commit()

    await callback.message.answer(
        f"✅ *Запис підтверджено!*\n\n"
        f"👤 {data['client_name']} ({data['client_phone']})\n"
        f"🔍 {services_dict[data['service']]}\n"
        f"👩‍🎨 {masters_dict[data['master']]}\n"
        f"📅 {date_text}\n"
        f"🕐 {time_text}",
        parse_mode="Markdown",
        reply_markup=kb.admin_kb
    )

    await state.clear()
    await callback.answer()

@user.callback_query(lambda c: c.data == "admin_confirm_no")
async def admin_confirm_no(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        "❌ Запис скасовано",
        reply_markup=kb.admin_kb
    )
    await callback.answer()

@user.callback_query(lambda c: c.data == "admin_delete")
async def admin_delete_callback(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Немає доступу", show_alert=True)
        return

    await state.set_state(AdminAction.waiting_for_delete_id)
    await callback.message.answer("Введіть ID запису для видалення:")
    await callback.answer()

@user.callback_query(lambda c: c.data == "admin_delete")
async def admin_delete_callback(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Немає доступу", show_alert=True)
        return
    await state.set_state(AdminAction.waiting_for_delete_id)
    await callback.message.answer("Введіть ID запису для видалення:")
    await callback.answer()

# ← одразу після додай це:
@user.message(AdminAction.waiting_for_delete_id)
async def process_delete_booking(message: Message, state: FSMContext):
    text = message.text.strip()
    if not text.isdigit():
        await message.answer("❌ Введіть числовий ID запису")
        return
    booking_id = int(text)
    cursor.execute("SELECT * FROM bookings WHERE id = %s", (booking_id,))
    if not cursor.fetchone():
        await message.answer("❌ Запис з таким ID не знайдено")
        await state.clear()
        return
    cursor.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))
    conn.commit()
    await message.answer(f"🗑 Запис #{booking_id} видалено", reply_markup=kb.admin_kb)
    await state.clear()

@user.callback_query(lambda c: c.data == "admin_stats")
async def admin_stats_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Немає доступу", show_alert=True)
        return

    cursor.execute("""
        SELECT service, COUNT(*) 
        FROM bookings
        GROUP BY service
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """)
    service = cursor.fetchone()

    cursor.execute("""
        SELECT master, COUNT(*) 
        FROM bookings
        GROUP BY master
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """)
    master = cursor.fetchone()

    cursor.execute("SELECT ROUND(AVG(rating), 1) FROM reviews")
    avg_rating = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reviews")
    reviews_count = cursor.fetchone()[0]

    ratings = {}

    for i in range(1, 6):
        cursor.execute(
            "SELECT COUNT(*) FROM reviews WHERE rating=%s",
            (i,)
        )
        ratings[i] = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users")
    clients_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM bookings")
    bookings_count = cursor.fetchone()[0]

    text = "📊 *Статистика:*\n\n"
    text += f"👥 Клієнтів: {clients_count}\n"
    text += f"📋 Записів: {bookings_count}\n\n"
    text += f"\n⭐ Середня оцінка салону: {avg_rating or 0}\n"
    text += f"💬 Відгуків отримано: {reviews_count}\n\n"

    text += f"😡 1★ — {ratings[1]}\n"
    text += f"😕 2★ — {ratings[2]}\n"
    text += f"😐 3★ — {ratings[3]}\n"
    text += f"🙂 4★ — {ratings[4]}\n"
    text += f"😃 5★ — {ratings[5]}\n"

    if service:
        text += f"🔥 Популярна послуга: {services_dict.get(service[0], service[0])} ({service[1]})\n"
    if master:
        text += f"👑 Топ майстер: {masters_dict.get(master[0], master[0])} ({master[1]})\n"

    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

@user.callback_query(lambda c: c.data == "admin_reviews")
async def admin_reviews(callback: CallbackQuery):
    cursor.execute("""
    SELECT users.name, reviews.rating, reviews.review_text
    FROM reviews
    JOIN users ON reviews.user_id = users.tg_id
    ORDER BY reviews.id DESC
    """)

    reviews = cursor.fetchall()

    if not reviews:
        await callback.message.answer("❌ Відгуків поки немає")
        await callback.answer()
        return

    text = "⭐ *Відгуки клієнтів:*\n\n"

    for name, rating, review_text in reviews:
        text += f"👤 {name}\n"
        text += f"{'⭐' * rating}\n"

        if review_text:
            text += f"💬 {review_text}\n"

        text += "--------------------\n"

    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

@user.callback_query(lambda c: c.data == "admin_bookings")
async def admin_bookings(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Немає доступу", show_alert=True)
        return

    cursor.execute("""
        SELECT bookings.id, users.name, users.phone, bookings.service, 
               bookings.master, bookings.date, bookings.time
        FROM bookings
        JOIN users ON bookings.user_id = users.id
    """)
    bookings = cursor.fetchall()

    if not bookings:
        await callback.message.answer("❌ Немає записів")
        await callback.answer()
        return

    text = "📋 *Записи:*\n\n"
    for b in bookings:
        booking_id, name, phone, service, master, date, time = b
        text += (
            f"🆔 #{booking_id}\n"
            f"👤 {name} ({phone})\n"
            f"🔍 {services_dict.get(service, service)}\n"
            f"👩‍🎨 {masters_dict.get(master, master)}\n"
            f"📅 {date} | {time}\n"
            f"------------------\n"
        )

    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

@user.callback_query(lambda c: c.data == "admin_bookings_future")
async def admin_bookings_future(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Немає доступу", show_alert=True)
        return

    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M")

    cursor.execute("""
        SELECT bookings.id, users.name, users.phone, bookings.service,
               bookings.master, bookings.date, bookings.time
        FROM bookings
        JOIN users ON bookings.user_id = users.id
        WHERE (
            bookings.date > %s
            OR (bookings.date = %s AND bookings.time > %s)
        )
        ORDER BY bookings.date, bookings.time
    """, (today, today, current_time))

    bookings = cursor.fetchall()

    if not bookings:
        await callback.message.answer("📭 Немає майбутніх записів")
        await callback.answer()
        return

    text = "📅 *Майбутні записи:*\n\n"
    for b in bookings:
        booking_id, name, phone, service, master, date, time = b
        text += (
            f"🆔 #{booking_id}\n"
            f"👤 {name} ({phone})\n"
            f"🔍 {services_dict.get(service, service)}\n"
            f"👩‍🎨 {masters_dict.get(master, master)}\n"
            f"📅 {date} | {time}\n"
            f"------------------\n"
        )

    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()

@user.callback_query(lambda c: c.data == "admin_clients")
async def admin_clients(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Немає доступу", show_alert=True)
        return

    cursor.execute("SELECT name, phone FROM users")
    users = cursor.fetchall()

    if not users:
        await callback.message.answer("❌ Немає клієнтів")
        await callback.answer()
        return

    text = "👥 *Клієнти:*\n\n"
    for u in users:
        text += f"👤 {u[0]} — {u[1]}\n"

    await callback.message.answer(text, parse_mode="Markdown")
    await callback.answer()


@user.callback_query(lambda c: c.data == "booking")
async def start_booking(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Booking.service)

    await callback.message.answer(
        "Добре! Почнемо запис 💖",
        reply_markup=ReplyKeyboardRemove()
    )
    await callback.message.answer(
        "🔍 Оберіть послугу 👇",
        reply_markup=kb.services_kb
    )
    await callback.answer()

@user.callback_query(lambda c: c.data.startswith("service_"))
async def choose_service(callback: CallbackQuery, state: FSMContext):
    service_key = callback.data

    await state.update_data(service=service_key)
    await state.set_state(Booking.master)

    await callback.message.answer(
        "👩‍🎨 Оберіть майстра 👇",
        reply_markup=kb.masters_kb
    )
    await callback.answer()


@user.callback_query(lambda c: c.data.startswith("master_"))
async def choose_master(callback: CallbackQuery, state: FSMContext):
    master_key = callback.data

    await state.update_data(master=master_key)
    await state.set_state(Booking.date)

    dates_dict = get_dates()

    await callback.message.answer(
        "📅 Оберіть дату 👇",
        reply_markup=kb.get_dates_kb(dates_dict)
    )
    await callback.answer()

def get_dates():
    months = {
        "01": "січня", "02": "лютого", "03": "березня",
        "04": "квітня", "05": "травня", "06": "червня",
        "07": "липня", "08": "серпня", "09": "вересня",
        "10": "жовтня", "11": "листопада", "12": "грудня"
    }

    weekdays = [
        "Понеділок", "Вівторок", "Середа",
        "Четвер", "П’ятниця", "Субота", "Неділя"
    ]

    dates = {}

    for i in range(5):
        day = datetime.now() + timedelta(days=i)

        key = f"date_{i}"
        value = f"{weekdays[day.weekday()]}, {day.strftime('%d')} {months[day.strftime('%m')]}"

        dates[key] = value

    return dates

dates_dict = get_dates()

def get_times(selected_date_key):
    times = {}
    now = datetime.now()

    selected_date = datetime.now() + timedelta(days=int(selected_date_key.split("_")[1]))

    for hour in range(10, 20):
        key = f"time_{hour}"
        value = f"{hour}:00"

        if selected_date.date() == now.date():
            if hour <= now.hour:
                continue

        times[key] = value

    return times

def get_free_times(master, date_key):
    all_times = get_times(date_key)

    real_date = (datetime.now() + timedelta(days=int(date_key.split("_")[1]))).strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT time FROM bookings
        WHERE master=%s AND date=%s
    """, (master, real_date))

    busy_times = [row[0] for row in cursor.fetchall()]

    free_times = {
        k: v for k, v in all_times.items()
        if v not in busy_times
    }

    return free_times

@user.callback_query(lambda c: c.data.startswith("date_"))
async def choose_date(callback: CallbackQuery, state: FSMContext):
    date_key = callback.data

    data = await state.get_data()

    if "master" not in data:
        await callback.message.answer("❌ Оберіть майстра ще раз")
        await callback.answer()
        return

    master = data["master"]

    await state.update_data(date=date_key)

    free_times = get_free_times(master, date_key)

    if not free_times:
        await callback.answer(
            "❌ Немає вільного часу, будь ласка оберіть іншу дату",
            show_alert=True
        )
        return

    await callback.message.answer(
        "🕐 Оберіть час 👇",
        reply_markup=kb.get_times_kb(free_times)
    )

    await state.set_state(Booking.time)
    await callback.answer()


@user.callback_query(lambda c: c.data.startswith("time_"))
async def choose_time(callback: CallbackQuery, state: FSMContext):
    time_key = callback.data

    data = await state.get_data()
    date_key = data["date"]

    all_times = get_times(date_key)
    time_text = all_times[time_key]

    await state.update_data(time=time_key)
    data = await state.get_data()

    await state.set_state(Booking.confirm)

    date_text = get_dates()[date_key]

    await callback.message.answer(
        f"📋 *Підтвердіть запис:*\n\n"
        f"🔍 {services_dict[data['service']]}\n"
        f"👩‍🎨 {masters_dict[data['master']]}\n"
        f"📅 {date_text}\n"
        f"🕐 {time_text}\n\n"
        f"Все правильно? 👇",
        parse_mode="Markdown",
        reply_markup=kb.confirm_kb
    )

    await callback.answer()


@user.callback_query(lambda c: c.data == "confirm_yes")
async def confirm_yes(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    if "service" not in data:
        await callback.message.answer("❌ Помилка. Почніть запис заново")
        await callback.answer()
        return

    cursor.execute(
        "SELECT id FROM users WHERE tg_id = %s",
        (callback.from_user.id,)
    )
    user_row = cursor.fetchone()

    if not user_row:
        await callback.message.answer("❌ Користувача не знайдено")
        await callback.answer()
        return

    user_id = user_row[0]

    date_key = data["date"]
    time_key = data["time"]

    date_text = get_dates()[date_key]
    time_text = get_times(date_key)[time_key]

    real_date = (datetime.now() + timedelta(days=int(date_key.split("_")[1]))).strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT * FROM bookings 
        WHERE master=%s AND date=%s AND time=%s
    """, (data["master"], real_date, time_text))

    if cursor.fetchone():
        await callback.message.answer(
            "❌ Хтось щойно зайняв цей час. Оберіть інший 👇",
            reply_markup=kb.menu_front
        )
        await callback.answer()
        return

    cursor.execute(
        "INSERT INTO bookings (user_id, service, master, date, time) VALUES (%s, %s, %s, %s, %s)",
        (user_id, data["service"], data["master"], real_date, time_text)
    )
    conn.commit()

    await callback.message.answer(
        f"✅ *Запис підтверджено!*\n\n"
        f"🔍 {services_dict[data['service']]}\n"
        f"👩‍🎨 {masters_dict[data['master']]}\n"
        f"📅 {date_text}\n"
        f"🕐 {time_text}\n\n"
        f"🎉 Чекаємо на вас 💖",
        parse_mode="Markdown",
        reply_markup=kb.menu_front
    )

    await state.clear()
    await callback.answer()


@user.callback_query(lambda c: c.data == "confirm_no")
async def confirm_no(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "❌ Запис скасовано\n\nОберіть дію 👇",
        reply_markup=kb.menu_front
    )

    await state.clear()
    await callback.answer()

@user.callback_query(lambda c: c.data == "my_bookings")
async def my_bookings(callback: CallbackQuery):
    cursor.execute(
        "SELECT id FROM users WHERE tg_id = %s",
        (callback.from_user.id,)
    )
    user_row = cursor.fetchone()

    if not user_row:
        await callback.message.answer("❌ Ви ще не зареєстровані")
        await callback.answer()
        return

    user_id = user_row[0]
    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M")

    cursor.execute("""
        SELECT id, service, master, date, time FROM bookings 
        WHERE user_id = %s
        AND (
            date > %s 
            OR (date = %s AND time > %s)
        )
    """, (user_id, today, today, current_time))

    bookings = cursor.fetchall()

    if not bookings:
        await callback.message.answer(
            "📭 У вас немає активних записів",
            reply_markup=kb.menu_front
        )
        await callback.answer()
        return

    await callback.message.answer(
        "📋 *Ваші записи:*\n\nНатисніть на запис щоб скасувати його 👇",
        parse_mode="Markdown",
        reply_markup=kb.my_bookings_kb(bookings, services_dict)
    )
    await callback.answer()


@user.callback_query(lambda c: c.data.startswith("cancel_booking_"))
async def cancel_booking_confirm(callback: CallbackQuery):
    booking_id = int(callback.data.split("_")[-1])

    cursor.execute(
        "SELECT service, master, date, time FROM bookings WHERE id = %s",
        (booking_id,)
    )
    booking = cursor.fetchone()

    if not booking:
        await callback.message.answer("❌ Запис не знайдено")
        await callback.answer()
        return

    service, master, date, time = booking

    await callback.message.answer(
        f"⚠️ *Скасувати цей запис?*\n\n"
        f"🔍 {services_dict.get(service, service)}\n"
        f"👩‍🎨 {masters_dict.get(master, master)}\n"
        f"📅 {date}\n"
        f"🕐 {time}",
        parse_mode="Markdown",
        reply_markup=kb.confirm_cancel_kb(booking_id)
    )
    await callback.answer()

@user.callback_query(lambda c: c.data.startswith("confirm_cancel_"))
async def confirm_cancel_booking(callback: CallbackQuery):
    booking_id = int(callback.data.split("_")[-1])

    cursor.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))
    conn.commit()

    await callback.message.edit_text(
        "✅ Запис скасовано\n\nБудемо чекати вас наступного разу 💖"
    )
    await callback.message.answer(
        "Оберіть дію 👇",
        reply_markup=kb.menu_front
    )
    await callback.answer()


# Кнопка "Назад" до меню
@user.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    await callback.message.answer(
        "Оберіть дію 👇",
        reply_markup=kb.menu_front
    )
    await callback.answer()

@user.message(Command("booking"))
async def booking_cmd(message: Message, state: FSMContext):
    await state.set_state(Booking.service)
    await message.answer("🔍 Оберіть послугу 👇", reply_markup=kb.services_kb)

@user.message(Command("my_bookings"))
async def my_bookings_cmd(message: Message):
    cursor.execute(
        "SELECT id FROM users WHERE tg_id = %s",
        (message.from_user.id,)
    )
    user_row = cursor.fetchone()

    if not user_row:
        await message.answer("❌ Ви ще не зареєстровані")
        return

    user_id = user_row[0]
    today = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M")

    cursor.execute("""
        SELECT id, service, master, date, time FROM bookings 
        WHERE user_id = %s
        AND (
            date > %s 
            OR (date = %s AND time > %s)
        )
    """, (user_id, today, today, current_time))

    bookings = cursor.fetchall()

    if not bookings:
        await message.answer(
            "📭 У вас немає активних записів",
            reply_markup=kb.menu_front
        )
        return

    await message.answer(
        "📋 *Ваші записи:*\n\nНатисніть на запис щоб скасувати його 👇",
        parse_mode="Markdown",
        reply_markup=kb.my_bookings_kb(bookings, services_dict)
    )

@user.callback_query(lambda c: c.data == "price")
async def price(callback: CallbackQuery):
    await callback.message.answer(
        "💰 Прайс тут 👇 \n\n(Ваш прайс)",
        reply_markup=ReplyKeyboardRemove()
    )
    await callback.answer()

@user.message(Command("price"))
async def price_cmd(message: Message):
    await message.answer("💰 Прайс тут 👇 \n\n(Ваш прайс)")


@user.callback_query(lambda c: c.data == "masters")
async def masters(callback: CallbackQuery):
    photo1 = FSInputFile("images/masters.jpg")
    photo2 = FSInputFile("images/masters.jpg")

    await callback.message.answer_photo(
        photo=photo1,
        caption="(Ваш майстер). Приклад: \n\nАнна — майстер манікюру\nДосвід: 3 роки\nТоп-майстер"
    )

    await callback.message.answer_photo(
        photo=photo2,
        caption="(Ваш майстер). Приклад: \n\nОлена — перукар\nДосвід: 5 років\nКолорист"
    )

    await callback.answer()

@user.message(Command("masters"))
async def masters_cmd(message: Message):
    photo1 = FSInputFile("images/masters.jpg")
    photo2 = FSInputFile("images/masters.jpg")
    await message.answer_photo(
        photo=photo1,
        caption="(Ваш майстер). Приклад: \n\nАнна — майстер манікюру\nДосвід: 3 роки\nТоп-майстер"
    )
    await message.answer_photo(
        photo=photo2,
        caption="(Ваш майстер). Приклад: \n\nОлена — перукар\nДосвід: 5 років\nКолорист"
    )

@user.callback_query(lambda c: c.data == "adresses")
async def adresses(callback: CallbackQuery):
    await callback.message.answer(
        "📍 Наша адреса:\n(ваша адреса)\n\nНатисніть кнопку нижче, щоб відкрити карту",
        reply_markup=kb.location_kb
    )
    await callback.answer()

@user.message(Command("address"))
async def address_cmd(message: Message):
    await message.answer("📍 Наша адреса:\n(ваша адреса)\n\nНатисніть кнопку нижче, щоб відкрити карту",
                         reply_markup=kb.location_kb)

@user.callback_query(lambda c: c.data == "contacts")
async def contacts(callback: CallbackQuery):
    await callback.message.answer(
        "📞 Наші контакти: \n\n(Ваші контакти)",
        reply_markup=ReplyKeyboardRemove()
    )
    await callback.answer()

@user.message(Command("contacts"))
async def contacts_cmd(message: Message):
    await message.answer("📞 Наші контакти: \n\n(Ваші контакти)")

@user.callback_query(lambda c: c.data == "schedule")
async def schedule(callback: CallbackQuery):
    await callback.message.answer(
        "🕒 Чекаємо на вас щодня: \n\n(Ваш графік)\nОберіть свій ідеальний час ☕️",
        reply_markup=ReplyKeyboardRemove()
    )
    await callback.answer()

@user.message(Command("schedule"))
async def schedule_cmd(message: Message):
    await message.answer("🕒 Чекаємо на вас щодня: \n\n(Ваш графік)\nОберіть свій ідеальний час ☕️")

@user.callback_query(lambda c: c.data == "reviews")
async def reviews(callback: CallbackQuery):
    await callback.message.answer(
        "⭐ *Почитайте відгуки наших клієнтів: *\n\n"
        "Ми дбаємо про якість і сервіс 💖",
        parse_mode="Markdown",
        reply_markup=reviews_kb
    )
    await callback.answer()

@user.message(Command("reviews"))
async def reviews_cmd(message: Message):
    await message.answer("⭐ *Почитайте відгуки наших клієнтів: *\n\n"
        "Ми дбаємо про якість і сервіс 💖", reply_markup=reviews_kb)

@user.callback_query(lambda c: c.data == "shares")
async def shares(callback: CallbackQuery):
    await callback.message.answer(
        "🎁 *Спеціальні пропозиції:*\n\n(Ваші акції)",
        parse_mode="Markdown",
        reply_markup=kb.shares_kb
    )
    await callback.answer()

@user.message(Command("shares"))
async def shares_cmd(message: Message):
    await message.answer("🎁 *Спеціальні пропозиції:*\n\n(Ваші акції)", reply_markup=kb.shares_kb)

@user.callback_query(lambda c: c.data == "faq")
async def faq(callback: CallbackQuery):
    await callback.message.answer(
        "❓ *Часті питання:*\n\n(Ваші питання-відповіді)\n\n Приклад:\n\n"

        "💬 Як записатися?\n"
        "— Через кнопку «Записатися»\n\n"
        
        "👇 Не знайшли відповідь? Напишіть нам",

        parse_mode="Markdown",
        reply_markup=kb.faq_kb
    )
    await callback.answer()

@user.message(Command("faq"))
async def faq_cmd(message: Message):
    await message.answer("❓ *Часті питання:*\n\n(Ваші питання-відповіді)\n\n Приклад:\n\n"

        "💬 Як записатися?\n"
        "— Через кнопку «Записатися»\n\n"
        
        "👇 Не знайшли відповідь? Напишіть нам", reply_markup=kb.faq_kb)



@user.callback_query(lambda c: c.data.startswith("rating_"))
async def save_rating(callback: CallbackQuery, state: FSMContext):

    rating = int(callback.data.split("_")[1])

    await state.update_data(rating=rating)

    await callback.message.answer(
        f"Дякуємо за оцінку {'⭐' * rating}\n\n"
        f"Бажаєте залишити коментар?",
        reply_markup=kb.review_choice_kb
    )

    await callback.answer()

@user.callback_query(lambda c: c.data == "review_yes")
async def review_yes(callback: CallbackQuery, state: FSMContext):

    await callback.message.answer(
        "✍️ Напишіть ваш коментар:"
    )

    await state.set_state(Review.text)
    await callback.answer()

@user.callback_query(lambda c: c.data == "review_no")
async def review_no(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()

    cursor.execute(
        """
        INSERT INTO reviews (user_id, rating)
        VALUES (%s, %s)
        """,
        (
            callback.from_user.id,
            data["rating"]
        )
    )

    conn.commit()

    await state.clear()

    await callback.message.answer(
        "💖 Дякуємо за ваш відгук!"
    )

    await callback.answer()

@user.message(Review.text)
async def save_review_text(message: Message, state: FSMContext):

    data = await state.get_data()

    cursor.execute(
        """
        INSERT INTO reviews (user_id, rating, review_text)
        VALUES (%s, %s, %s)
        """,
        (
            message.from_user.id,
            data["rating"],
            message.text
        )
    )

    conn.commit()

    await state.clear()

    await message.answer(
        "💖 Дякуємо за ваш відгук!"
    )

# @user.message(Command("test_scheduler"))
# async def test_scheduler(message: Message):
#     if not is_admin(message.from_user.id):
#         await message.answer("❌ Немає доступу")
#         return
#
#     bot = message.bot
#
#     await message.answer("🔄 Запускаємо тест...")
#
#     await send_afternoon_reminders(bot)
#     await message.answer("✅ send_afternoon_reminders — виконано")
#
#     await send_hour_before_reminders(bot)
#     await message.answer("✅ send_hour_before_reminders — виконано")
#
#     await send_review_requests(bot)
#     await message.answer("✅ send_review_requests — виконано")
#
#     await message.answer("🏁 Тест завершено")
#
# @user.message(Command("test_booking"))
# async def test_booking(message: Message):
#     if not is_admin(message.from_user.id):
#         await message.answer("❌ Немає доступу")
#         return
#
#     now = datetime.now()
#
#     # Запис "завтра" для тесту нагадування о 14:00
#     tomorrow = (now + timedelta(days=1)).strftime("%Y-%m-%d")
#     tomorrow_time = "14:00"
#
#     # Запис через 1 годину для тесту нагадування перед візитом
#     hour_later = (now + timedelta(minutes=60)).strftime("%H:%M")
#
#     # Запис 2 години тому для тесту відгуку
#     two_hours_ago = (now - timedelta(minutes=130)).strftime("%H:%M")
#     today = now.strftime("%Y-%m-%d")
#
#     cursor.execute("SELECT id FROM users WHERE tg_id = ?", (message.from_user.id,))
#     user_row = cursor.fetchone()
#
#     if not user_row:
#         await message.answer("❌ Користувача не знайдено")
#         return
#
#     user_id = user_row[0]
#
#     # Додаємо 3 тестові записи
#     cursor.execute(
#         "INSERT INTO bookings (user_id, service, master, date, time) VALUES (?, ?, ?, ?, ?)",
#         (user_id, "service_1", "master_1", tomorrow, tomorrow_time)
#     )
#     cursor.execute(
#         "INSERT INTO bookings (user_id, service, master, date, time) VALUES (?, ?, ?, ?, ?)",
#         (user_id, "service_1", "master_1", today, hour_later)
#     )
#     cursor.execute(
#         "INSERT INTO bookings (user_id, service, master, date, time) VALUES (?, ?, ?, ?, ?)",
#         (user_id, "service_1", "master_1", today, two_hours_ago)
#     )
#     conn.commit()
#
#     await message.answer(
#         f"✅ Тестові записи додано:\n\n"
#         f"1. Завтра о {tomorrow_time} — для нагадування о 14:00\n"
#         f"2. Сьогодні о {hour_later} — для нагадування за годину\n"
#         f"3. Сьогодні о {two_hours_ago} — для запиту відгуку\n\n"
#         f"Тепер запусти /test_scheduler"
#     )

@user.message()
async def unknown_message(message: Message):
    await message.answer(
        "🤔 Я вас не розумію\n\nБудь ласка, оберіть дію з меню 👇",
        reply_markup=kb.menu_front
    )