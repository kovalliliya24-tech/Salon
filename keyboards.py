from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)


menu_front = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📅 Записатися", callback_data="booking")],
        [InlineKeyboardButton(text="🗑 Мої записи", callback_data="my_bookings")],
        [InlineKeyboardButton(text="💰 Прайс", callback_data="price")],
        [InlineKeyboardButton(text="👩‍🎨 Майстри", callback_data="masters")],
        [InlineKeyboardButton(text="📍 Адреса", callback_data="adresses")],
        [InlineKeyboardButton(text="📞 Контакти", callback_data="contacts")],
        [InlineKeyboardButton(text="🕒 Графік роботи", callback_data="schedule")],
        [InlineKeyboardButton(text="⭐ Відгуки клієнтів", callback_data="reviews")],
        [InlineKeyboardButton(text="🎁 Акції", callback_data="shares")],
        [InlineKeyboardButton(text="❓ FAQ", callback_data="faq")]
    ],
    resize_keyboard = True
)

get_number = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='📱 Надіслати номер', request_contact=True)]
    ],
    resize_keyboard = True
)

services_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💝 Ваша послуга - ваша ціна", callback_data="service_1")],
        [InlineKeyboardButton(text="💝 Ваша послуга - ваша ціна", callback_data="service_2")],
        [InlineKeyboardButton(text="💝 Ваша послуга - ваша ціна", callback_data="service_3")],
    ]
)

masters_kb = InlineKeyboardMarkup(
    inline_keyboard=[
         [InlineKeyboardButton(text="👩‍🎨 Ваш майстер",  callback_data="master_1")],
         [InlineKeyboardButton(text="👩‍🎨 Ваш майстер",  callback_data="master_2")],
         [InlineKeyboardButton(text="👩‍🎨 Ваш майстер",  callback_data="master_3")]
     ]
 )

dates_kb = InlineKeyboardMarkup(
    inline_keyboard=[
         [InlineKeyboardButton(text="👩 25 березня", callback_data="date_25")],
         [InlineKeyboardButton(text="👩 26 березня", callback_data="date_26")]
     ]
 )

times_kb = InlineKeyboardMarkup(
    inline_keyboard=[
         [InlineKeyboardButton(text="🕒 10:00", callback_data="time_10")],
         [InlineKeyboardButton(text="🕒 11:00", callback_data="time_11")]
     ]
 )

confirm_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Підтвердити", callback_data="confirm_yes"),
            InlineKeyboardButton(text="❌ Скасувати", callback_data="confirm_no")
        ]
    ]
)

location_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text="📍 Відкрити мапу",
            url="https://maps.google.com/?q=Київ"
        )]
    ]
)

reviews_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text="📸 Переглянути всі відгуки",
            url="https://www.instagram.com/"
        )]
    ]
)

shares_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📅 Записатися", callback_data="booking")],
        [InlineKeyboardButton(text="🔥 Більше акцій", url="https://www.instagram.com/")],
    ]
)
faq_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💬 Написати нам", url="https://www.instagram.com/")]
    ]
)

admin_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📊 Всі записи", callback_data="admin_bookings")],
    [InlineKeyboardButton(text="📅 Майбутні записи", callback_data="admin_bookings_future")],
    [InlineKeyboardButton(text="👥 Клієнти", callback_data="admin_clients")],
    [InlineKeyboardButton(text="⭐ Відгуки",callback_data="admin_reviews")],
    [InlineKeyboardButton(text="📈 Статистика", callback_data="admin_stats")],
    [InlineKeyboardButton(text="➕ Додати запис", callback_data="admin_add")],
    [InlineKeyboardButton(text="❌ Видалити запис", callback_data="admin_delete")],
    [InlineKeyboardButton(text="❌ Очистити всі записи", callback_data="admin_delete_all")]
])

confirm_delete_all_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Так, видалити всі", callback_data="confirm_delete_all"),
            InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel_delete_all")
        ]
    ]
)

rating_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⭐", callback_data="rating_1")],
        [InlineKeyboardButton(text="⭐⭐", callback_data="rating_2")],
        [InlineKeyboardButton(text="⭐⭐⭐", callback_data="rating_3")],
        [InlineKeyboardButton(text="⭐⭐⭐⭐", callback_data="rating_4")],
        [InlineKeyboardButton(text="⭐⭐⭐⭐⭐", callback_data="rating_5")]
    ]
)
review_choice_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Так", callback_data="review_yes"),
            InlineKeyboardButton(text="❌ Ні", callback_data="review_no")
        ]
    ]
)

def get_dates_kb(dates_dict):
    keyboard = []

    for key, value in dates_dict.items():
        keyboard.append([InlineKeyboardButton(text=value, callback_data=key)])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_times_kb(free_times):
    buttons = []

    for key, value in free_times.items():
        buttons.append(
            [InlineKeyboardButton(text=value, callback_data=key)]
        )

    if not buttons:
        buttons.append(
            [InlineKeyboardButton(text="❌ Немає вільного часу", callback_data="no_time")]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def delete_booking_kb(booking_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="❌ Видалити",
            callback_data=f"delete_{booking_id}"
        )]
    ])

def my_bookings_kb(bookings, services_dict):
    keyboard = []
    for b in bookings:
        booking_id, service, master, date, time = b
        label = f"❌ {services_dict.get(service, service)} | {date} {time}"
        keyboard.append([
            InlineKeyboardButton(text=label, callback_data=f"cancel_booking_{booking_id}")
        ])
    keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def confirm_cancel_kb(booking_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Так, скасувати", callback_data=f"confirm_cancel_{booking_id}"),
            InlineKeyboardButton(text="🔙 Назад", callback_data="my_bookings")
        ]
    ])

def admin_confirm_yes_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Підтвердити", callback_data="admin_confirm_yes"),
            InlineKeyboardButton(text="❌ Скасувати", callback_data="admin_confirm_no")
        ]
    ])


