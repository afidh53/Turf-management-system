from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import os

from models import (
    init_db,
    get_db,
    create_user,
    get_user_by_email,
    verify_user,
    list_turfs,
    create_booking,
    check_duplicate_booking,
    get_bookings_by_user,
    cancel_booking,
    get_all_users,
    delete_user,
    get_all_bookings,
    delete_booking,
    search_bookings,
    filter_bookings_by_date,
    update_booking_status,
    get_admin_stats,
)


app = Flask(__name__)
app.config.from_object('config.Config')


@app.before_first_request
def setup():
    init_db()


def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated


@app.route('/')
def index():
    turfs = list_turfs()
    return render_template('index.html', turfs=turfs)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip().lower()
        phone = request.form['phone'].strip()
        password = request.form['password']
        confirm = request.form['confirm']

        if not name or not email or not phone or not password:
            flash('Please fill all required fields', 'warning')
            return render_template('register.html')

        if password != confirm:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')

        if get_user_by_email(email):
            flash('Email already registered', 'danger')
            return render_template('register.html')

        pw_hash = generate_password_hash(password)
        create_user(name, email, phone, pw_hash)
        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        user = get_user_by_email(email)
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            flash('Logged in successfully', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    turfs = list_turfs()
    return render_template('dashboard.html', turfs=turfs)


@app.route('/booking/<turf_name>', methods=['GET', 'POST'])
@login_required
def booking(turf_name):
    turfs = list_turfs()
    turf = next((t for t in turfs if t['name'] == turf_name), None)
    if not turf:
        flash('Turf not found', 'danger')
        return redirect(url_for('dashboard'))

    time_slots = [
        '6 AM - 7 AM',
        '7 AM - 8 AM',
        '8 AM - 9 AM',
        '4 PM - 5 PM',
        '5 PM - 6 PM',
        '6 PM - 7 PM',
        '7 PM - 8 PM',
    ]

    if request.method == 'POST':
        booking_date = request.form['booking_date']
        time_slot = request.form['time_slot']
        if not booking_date or not time_slot:
            flash('Please select date and time slot', 'warning')
            return render_template('booking.html', turf=turf, time_slots=time_slots)

        # validate date
        try:
            bdate = datetime.strptime(booking_date, '%Y-%m-%d').date()
            if bdate < date.today():
                flash('Booking date cannot be in the past', 'danger')
                return render_template('booking.html', turf=turf, time_slots=time_slots)
        except ValueError:
            flash('Invalid date format', 'danger')
            return render_template('booking.html', turf=turf, time_slots=time_slots)

        user_id = session['user_id']
        if check_duplicate_booking(turf_name, booking_date, time_slot):
            flash('Slot Already Booked', 'danger')
            return render_template('booking.html', turf=turf, time_slots=time_slots)

        create_booking(user_id, turf_name, booking_date, time_slot)
        flash('Booking confirmed', 'success')
        return redirect(url_for('my_bookings'))

    return render_template('booking.html', turf=turf, time_slots=time_slots)


@app.route('/my_bookings')
@login_required
def my_bookings():
    user_id = session['user_id']
    bookings = get_bookings_by_user(user_id)
    return render_template('my_bookings.html', bookings=bookings)


@app.route('/cancel_booking/<int:booking_id>')
@login_required
def cancel(booking_id):
    user_id = session['user_id']
    cancel_booking(booking_id, user_id)
    flash('Booking cancelled', 'info')
    return redirect(url_for('my_bookings'))


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == app.config['ADMIN_USER'] and password == app.config['ADMIN_PASS']:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        flash('Invalid admin credentials', 'danger')
    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    flash('Admin logged out', 'info')
    return redirect(url_for('index'))


def admin_required(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)

    return decorated


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    stats = get_admin_stats()
    return render_template('admin_dashboard.html', stats=stats)


@app.route('/admin/users')
@admin_required
def admin_users():
    users = get_all_users()
    return render_template('users.html', users=users)


@app.route('/admin/delete_user/<int:user_id>')
@admin_required
def admin_delete_user(user_id):
    delete_user(user_id)
    flash('User deleted', 'info')
    return redirect(url_for('admin_users'))


@app.route('/admin/bookings', methods=['GET', 'POST'])
@admin_required
def admin_bookings():
    bookings = get_all_bookings()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'search':
            q = request.form.get('q', '').strip()
            bookings = search_bookings(q)
        elif action == 'filter':
            fdate = request.form.get('fdate')
            bookings = filter_bookings_by_date(fdate)
    return render_template('bookings.html', bookings=bookings)


@app.route('/admin/delete_booking/<int:booking_id>')
@admin_required
def admin_delete_booking(booking_id):
    delete_booking(booking_id)
    flash('Booking deleted', 'info')
    return redirect(url_for('admin_bookings'))


@app.route('/admin/update_status/<int:booking_id>', methods=['POST'])
@admin_required
def admin_update_status(booking_id):
    status = request.form.get('status')
    update_booking_status(booking_id, status)
    flash('Status updated', 'success')
    return redirect(url_for('admin_bookings'))


if __name__ == '__main__':
    app.run(debug=True)
