-- SQL initialization for Turf Management System
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  phone TEXT,
  password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS bookings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER,
  turf_name TEXT,
  booking_date TEXT,
  time_slot TEXT,
  status TEXT DEFAULT 'Booked',
  FOREIGN KEY(user_id) REFERENCES users(id)
);
