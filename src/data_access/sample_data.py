"""Seed utilities for development."""
from __future__ import annotations

import sqlite3

from flask import current_app
from werkzeug.security import generate_password_hash

SEED_USERS = [
    {
        'name': 'Admin Rivera',
        'email': 'admin@campus.test',
        'password_hash': generate_password_hash('AdminPass1!'),
        'role': 'admin',
        'department': 'Central IT',
    },
    {
        'name': 'Staff Chen',
        'email': 'staff@campus.test',
        'password_hash': generate_password_hash('StaffPass1!'),
        'role': 'staff',
        'department': 'Library',
    },
    {
        'name': 'Student Malik',
        'email': 'student@campus.test',
        'password_hash': generate_password_hash('StudentPass1!'),
        'role': 'student',
        'department': 'Engineering',
    },
]

SEED_RESOURCES = [
    {
        'title': 'Innovation Loft',
        'summary': 'Flexible project lab equipped with whiteboards, projection, and modular furniture for design sprints.',
        'category': 'Study Room',
        'location': 'Wells Library 4th Floor',
        'capacity': 10,
        'availability_notes': 'Weekdays 8a-10p; request 24h notice for staff assistance.',
        'status': 'published'
    },
    {
        'title': 'Audio Storytelling Kit',
        'summary': 'Portable microphones, mixers, and headphones ideal for podcasts or interview projects.',
        'category': 'AV Equipment',
        'location': 'Media Commons',
        'capacity': 3,
        'availability_notes': 'Pick up after 9a; return next business day.',
        'status': 'published'
    },
]


def ensure_seed_data():
    database_path = current_app.config['DATABASE_PATH']
    conn = sqlite3.connect(database_path)
    conn.row_factory = sqlite3.Row

    user_count = conn.execute('SELECT COUNT(*) AS total FROM users').fetchone()['total']
    if user_count == 0:
        for user in SEED_USERS:
            conn.execute(
                'INSERT INTO users (name, email, password_hash, role, department, email_verified) VALUES (?, ?, ?, ?, ?, 1)',
                (user['name'], user['email'], user['password_hash'], user['role'], user['department'])
            )
        conn.commit()

    resource_count = conn.execute('SELECT COUNT(*) AS total FROM resources').fetchone()['total']
    if resource_count == 0:
        owner_row = conn.execute('SELECT user_id FROM users WHERE email = ?', ('staff@campus.test',)).fetchone()
        owner_id = owner_row['user_id'] if owner_row else 1
        for res in SEED_RESOURCES:
            conn.execute(
                '''INSERT INTO resources (owner_id, title, summary, category, location, capacity, availability_notes, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (owner_id, res['title'], res['summary'], res['category'], res['location'], res['capacity'], res['availability_notes'], res['status'])
            )
        conn.commit()

    booking_total = conn.execute('SELECT COUNT(*) AS total FROM bookings').fetchone()['total']
    if booking_total == 0:
        student_id = conn.execute('SELECT user_id FROM users WHERE email = ?', ('student@campus.test',)).fetchone()['user_id']
        resource_id = conn.execute('SELECT resource_id FROM resources LIMIT 1').fetchone()['resource_id']
        conn.execute(
            '''INSERT INTO bookings (resource_id, requester_id, start_datetime, end_datetime, status, notes)
               VALUES (?, ?, ?, ?, 'approved', ?)''',
            (resource_id, student_id, '2025-01-10T10:00:00', '2025-01-10T12:00:00', 'Orientation walk-through')
        )
        conn.commit()

    review_total = conn.execute('SELECT COUNT(*) AS total FROM reviews').fetchone()['total']
    if review_total == 0:
        student_id = conn.execute('SELECT user_id FROM users WHERE email = ?', ('student@campus.test',)).fetchone()['user_id']
        resource_id = conn.execute('SELECT resource_id FROM resources LIMIT 1').fetchone()['resource_id']
        conn.execute(
            'INSERT INTO reviews (resource_id, reviewer_id, rating, comment) VALUES (?, ?, ?, ?)',
            (resource_id, student_id, 5, 'Great collaboration space with plenty of whiteboards.')
        )
        conn.commit()

    thread_total = conn.execute('SELECT COUNT(*) AS total FROM message_threads').fetchone()['total']
    if thread_total == 0:
        staff_id = conn.execute('SELECT user_id FROM users WHERE email = ?', ('staff@campus.test',)).fetchone()['user_id']
        student_id = conn.execute('SELECT user_id FROM users WHERE email = ?', ('student@campus.test',)).fetchone()['user_id']
        resource_id = conn.execute('SELECT resource_id FROM resources LIMIT 1').fetchone()['resource_id']
        cursor = conn.execute(
            'INSERT INTO message_threads (owner_id, participant_id, resource_id) VALUES (?, ?, ?)',
            (staff_id, student_id, resource_id)
        )
        thread_id = cursor.lastrowid
        conn.execute(
            'INSERT INTO messages (thread_id, sender_id, body) VALUES (?, ?, ?)',
            (thread_id, student_id, 'Hi! Is the loft available on Friday?')
        )
        conn.execute(
            'INSERT INTO messages (thread_id, sender_id, body) VALUES (?, ?, ?)',
            (thread_id, staff_id, 'Yes, please submit a booking and we will approve it.')
        )
        conn.commit()

    notification_total = conn.execute('SELECT COUNT(*) AS total FROM notifications').fetchone()['total']
    if notification_total == 0:
        staff_id = conn.execute('SELECT user_id FROM users WHERE email = ?', ('staff@campus.test',)).fetchone()['user_id']
        student_id = conn.execute('SELECT user_id FROM users WHERE email = ?', ('student@campus.test',)).fetchone()['user_id']
        conn.execute('INSERT INTO notifications (user_id, message) VALUES (?, ?)', (staff_id, 'Sample alert: booking queue awaiting review.'))
        conn.execute('INSERT INTO notifications (user_id, message) VALUES (?, ?)', (student_id, 'Sample alert: booking approved.'))
        conn.commit()

    conn.close()
