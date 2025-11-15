"""Booking data helpers."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from src.data_access.db import get_connection


@dataclass
class Booking:
    booking_id: int
    resource_id: int
    requester_id: int
    start_datetime: str
    end_datetime: str
    status: str
    notes: str | None
    owner_notes: str | None
    decision_at: str | None
    created_at: str


class BookingDAL:
    STATUSES = ('pending', 'approved', 'rejected', 'cancelled', 'completed')

    @staticmethod
    def _row(row) -> Optional[Booking]:
        if not row:
            return None
        return Booking(
            booking_id=row['booking_id'],
            resource_id=row['resource_id'],
            requester_id=row['requester_id'],
            start_datetime=row['start_datetime'],
            end_datetime=row['end_datetime'],
            status=row['status'],
            notes=row['notes'],
            owner_notes=row['owner_notes'],
            decision_at=row['decision_at'],
            created_at=row['created_at'],
        )

    @staticmethod
    def create_booking(resource_id: int, requester_id: int, start: str, end: str, notes: str | None, status: str = 'pending'):
        conn = get_connection()
        cursor = conn.execute(
            '''INSERT INTO bookings (resource_id, requester_id, start_datetime, end_datetime, status, notes)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (resource_id, requester_id, start, end, status, notes)
        )
        conn.commit()
        return BookingDAL.get_booking_by_id(cursor.lastrowid)

    @staticmethod
    def get_booking_by_id(booking_id: int) -> Optional[Booking]:
        conn = get_connection()
        row = conn.execute('SELECT * FROM bookings WHERE booking_id = ?', (booking_id,)).fetchone()
        return BookingDAL._row(row)

    @staticmethod
    def get_bookings_by_requester(user_id: int) -> List[Booking]:
        conn = get_connection()
        rows = conn.execute('SELECT * FROM bookings WHERE requester_id = ? ORDER BY start_datetime DESC', (user_id,)).fetchall()
        return [BookingDAL._row(row) for row in rows]

    @staticmethod
    def get_bookings_for_resource(resource_id: int) -> List[Booking]:
        conn = get_connection()
        rows = conn.execute('SELECT * FROM bookings WHERE resource_id = ? ORDER BY start_datetime DESC', (resource_id,)).fetchall()
        return [BookingDAL._row(row) for row in rows]

    @staticmethod
    def get_actionable_for_owner(owner_id: int) -> List[Booking]:
        conn = get_connection()
        rows = conn.execute(
            '''SELECT b.* FROM bookings b
               JOIN resources r ON r.resource_id = b.resource_id
               WHERE r.owner_id = ? AND b.status = 'pending'
               ORDER BY b.start_datetime ASC''',
            (owner_id,)
        ).fetchall()
        return [BookingDAL._row(row) for row in rows]

    @staticmethod
    def list_recent(limit: int = 15) -> List[Booking]:
        conn = get_connection()
        rows = conn.execute('SELECT * FROM bookings ORDER BY created_at DESC LIMIT ?', (limit,)).fetchall()
        return [BookingDAL._row(row) for row in rows]

    @staticmethod
    def update_status(booking_id: int, status: str, owner_notes: str | None = None):
        if status not in BookingDAL.STATUSES:
            raise ValueError('Invalid status supplied.')
        conn = get_connection()
        conn.execute(
            'UPDATE bookings SET status = ?, owner_notes = ?, decision_at = CURRENT_TIMESTAMP WHERE booking_id = ?',
            (status, owner_notes, booking_id)
        )
        conn.commit()

    @staticmethod
    def mark_completed_for_past_reservations(now_iso: str):
        conn = get_connection()
        conn.execute(
            '''UPDATE bookings
               SET status = 'completed'
               WHERE status = 'approved' AND end_datetime < ?''',
            (now_iso,)
        )
        conn.commit()

    @staticmethod
    def has_conflict(resource_id: int, start: str, end: str, exclude_booking_id: int | None = None) -> bool:
        conn = get_connection()
        query = '''SELECT 1 FROM bookings
                   WHERE resource_id = ?
                     AND status IN ('pending','approved')
                     AND NOT (end_datetime <= ? OR start_datetime >= ?)'''
        params = [resource_id, start, end]
        if exclude_booking_id:
            query += ' AND booking_id != ?'
            params.append(exclude_booking_id)
        row = conn.execute(query, tuple(params)).fetchone()
        return bool(row)
