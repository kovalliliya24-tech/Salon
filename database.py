import psycopg2
import os

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
conn.autocommit = False
cursor = conn.cursor()

def reset_connection():
    global conn, cursor
    try:
        conn.rollback()
    except:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        conn.autocommit = False
        cursor = conn.cursor()

def get_cursor():
    global conn, cursor
    try:
        cursor.execute("SELECT 1")
        cursor.fetchone()
    except (psycopg2.InterfaceError, psycopg2.OperationalError):
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        conn.autocommit = False
        cursor = conn.cursor()
    return cursor

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    tg_id BIGINT UNIQUE,
    name TEXT,
    phone TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    id SERIAL PRIMARY KEY,
    user_id BIGINT,
    service TEXT,
    master TEXT,
    date TEXT,
    time TEXT,
    status TEXT DEFAULT 'active',
    reminded_afternoon INTEGER DEFAULT 0,
    reminded_before INTEGER DEFAULT 0,
    reviewed INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS reviews (
    id SERIAL PRIMARY KEY,
    user_id BIGINT,
    booking_id INTEGER,
    rating INTEGER,
    review_text TEXT
)
""")

conn.commit()