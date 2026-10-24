# Turf Management System

Simple Flask application to manage turf bookings.

Requirements
- Python 3.8+
- See `requirements.txt`

Setup

1. Create a virtual environment and install dependencies:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2. Run the app:

```bash
python app.py
```

You can also use the convenience wrapper:

```bash
python manage.py runserver
```

The app will create the SQLite database automatically at `database/turf.db` on first run.

Testing

- Register a user at `/register`.
- Login and book turfs from the dashboard.
- Admin: visit `/admin/login` with username `admin` and password `admin123`.
