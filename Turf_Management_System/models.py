import sqlite3
from sqlite3 import Row
import os
from config import Config
from datetime import date


def get_db():
    db_path = Config.DB_PATH
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT,
            password TEXT NOT NULL
        )'''
    )

    cur.execute(
        '''CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            turf_name TEXT,
            booking_date TEXT,
            time_slot TEXT,
            status TEXT DEFAULT 'Booked',
            FOREIGN KEY(user_id) REFERENCES users(id)
        )'''
    )

    # seed turfs table as in-memory list (no table) - store default turfs images in static
    conn.commit()
    conn.close()


def create_user(name, email, phone, password_hash):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO users (name, email, phone, password) VALUES (?, ?, ?, ?)',
                (name, email, phone, password_hash))
    conn.commit()
    conn.close()


def get_user_by_email(email):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE email = ?', (email,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def verify_user(email, password_hash):
    user = get_user_by_email(email)
    if not user:
        return False
    return user['password'] == password_hash


def list_turfs():
    base = os.path.join('static', 'images')
    return [
        {
            'name': 'Football Turf',
            'price': '120',
            'description': 'Standard full-size football turf with floodlights.',
            'image': os.path.join(base, 'football.svg'),
        },
        {
            'name': 'Cricket Turf',
            'price': '150',
            'description': 'Professional cricket pitch with nets.',
            'image': os.path.join(base, 'cricket.svg'),
        },
        {
            'name': 'Badminton Court',
            'price': '60',
            'description': 'Indoor badminton court with synthetic flooring.',
            'image': os.path.join(base, 'badminton.svg'),
        },
    ]


def check_duplicate_booking(turf_name, booking_date, time_slot):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM bookings WHERE turf_name=? AND booking_date=? AND time_slot=? AND status<>?',
                (turf_name, booking_date, time_slot, 'Cancelled'))
    row = cur.fetchone()
    conn.close()
    return True if row else False


def create_booking(user_id, turf_name, booking_date, time_slot):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO bookings (user_id, turf_name, booking_date, time_slot) VALUES (?, ?, ?, ?)',
                (user_id, turf_name, booking_date, time_slot))
    conn.commit()
    conn.close()


def get_bookings_by_user(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM bookings WHERE user_id = ? ORDER BY booking_date DESC', (user_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def cancel_booking(booking_id, user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('UPDATE bookings SET status = ? WHERE id = ? AND user_id = ?', ('Cancelled', booking_id, user_id))
    conn.commit()
    conn.close()


def get_all_users():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT id, name, email, phone FROM users ORDER BY id DESC')
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_user(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM bookings WHERE user_id = ?', (user_id,))
    cur.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()


def get_all_bookings():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''SELECT b.id, b.user_id, u.name as user_name, u.email as user_email, b.turf_name, b.booking_date, b.time_slot, b.status
                   FROM bookings b LEFT JOIN users u ON b.user_id = u.id
                   ORDER BY b.booking_date DESC''')
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_booking(booking_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM bookings WHERE id = ?', (booking_id,))
    conn.commit()
    conn.close()


def search_bookings(query):
    q = f"%{query}%"
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''SELECT b.id, b.user_id, u.name as user_name, u.email as user_email, b.turf_name, b.booking_date, b.time_slot, b.status
                   FROM bookings b LEFT JOIN users u ON b.user_id = u.id
                   WHERE u.name LIKE ? OR u.email LIKE ? OR b.turf_name LIKE ?
                   ORDER BY b.booking_date DESC''', (q, q, q))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def filter_bookings_by_date(fdate):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''SELECT b.id, b.user_id, u.name as user_name, u.email as user_email, b.turf_name, b.booking_date, b.time_slot, b.status
                   FROM bookings b LEFT JOIN users u ON b.user_id = u.id
                   WHERE b.booking_date = ?
                   ORDER BY b.time_slot''', (fdate,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_booking_status(booking_id, status):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('UPDATE bookings SET status = ? WHERE id = ?', (status, booking_id))
    conn.commit()
    conn.close()


def get_admin_stats():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) as total_users FROM users')
    users = cur.fetchone()['total_users']
    cur.execute('SELECT COUNT(*) as total_bookings FROM bookings')
    bookings = cur.fetchone()['total_bookings']
    today = date.today().isoformat()
    cur.execute('SELECT COUNT(*) as todays FROM bookings WHERE booking_date = ?', (today,))
    todays = cur.fetchone()['todays']
    # available slots = total turfs * slots per day - booked slots for today
    slots_per_turf = 7
    total_turfs = 3
    cur.execute('SELECT COUNT(*) as booked_today FROM bookings WHERE booking_date = ?', (today,))
    booked_today = cur.fetchone()['booked_today']
    available_slots = total_turfs * slots_per_turf - booked_today
    conn.close()
    return {
        'total_users': users,
        'total_bookings': bookings,
        'todays_bookings': todays,
        'available_slots': available_slots,
    }
