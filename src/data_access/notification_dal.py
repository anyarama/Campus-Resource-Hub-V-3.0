"""Notification helpers."""
from __future__ import annotations

from typing import List

from src.data_access.db import get_connection


class NotificationDAL:
    @staticmethod
    def create_notification(user_id: int, message: str):
        conn = get_connection()
        conn.execute('INSERT INTO notifications (user_id, message) VALUES (?, ?)', (user_id, message))
        conn.commit()

    @staticmethod
    def list_for_user(user_id: int, limit: int = 10) -> List[dict]:
        conn = get_connection()
        rows = conn.execute(
            'SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT ?',
            (user_id, limit)
        ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def mark_all_read(user_id: int):
        conn = get_connection()
        conn.execute('UPDATE notifications SET is_read = 1 WHERE user_id = ?', (user_id,))
        conn.commit()
