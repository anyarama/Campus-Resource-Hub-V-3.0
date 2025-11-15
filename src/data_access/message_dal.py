"""Messaging data helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from src.data_access.db import get_connection


@dataclass
class MessageThread:
    thread_id: int
    resource_id: int | None
    owner_id: int
    participant_id: int
    created_at: str
    updated_at: str


@dataclass
class Message:
    message_id: int
    thread_id: int
    sender_id: int
    body: str
    created_at: str


class MessageDAL:
    @staticmethod
    def _thread_row(row) -> Optional[MessageThread]:
        if not row:
            return None
        return MessageThread(
            thread_id=row['thread_id'],
            resource_id=row['resource_id'],
            owner_id=row['owner_id'],
            participant_id=row['participant_id'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
        )

    @staticmethod
    def _message_row(row) -> Optional[Message]:
        if not row:
            return None
        return Message(
            message_id=row['message_id'],
            thread_id=row['thread_id'],
            sender_id=row['sender_id'],
            body=row['body'],
            created_at=row['created_at'],
        )

    @staticmethod
    def find_or_create_thread(owner_id: int, participant_id: int, resource_id: int | None = None) -> MessageThread:
        conn = get_connection()
        row = conn.execute(
            '''SELECT * FROM message_threads
               WHERE owner_id = ? AND participant_id = ? AND IFNULL(resource_id, 0) = IFNULL(?, 0)
               LIMIT 1''',
            (owner_id, participant_id, resource_id)
        ).fetchone()
        if row:
            return MessageDAL._thread_row(row)
        cursor = conn.execute(
            'INSERT INTO message_threads (owner_id, participant_id, resource_id) VALUES (?, ?, ?)',
            (owner_id, participant_id, resource_id)
        )
        conn.commit()
        return MessageDAL.get_thread_by_id(cursor.lastrowid)

    @staticmethod
    def get_thread_by_id(thread_id: int) -> Optional[MessageThread]:
        conn = get_connection()
        row = conn.execute('SELECT * FROM message_threads WHERE thread_id = ?', (thread_id,)).fetchone()
        return MessageDAL._thread_row(row)

    @staticmethod
    def list_threads_for_user(user_id: int) -> List[MessageThread]:
        conn = get_connection()
        rows = conn.execute(
            '''SELECT * FROM message_threads
               WHERE owner_id = ? OR participant_id = ?
               ORDER BY updated_at DESC''',
            (user_id, user_id)
        ).fetchall()
        return [MessageDAL._thread_row(row) for row in rows]

    @staticmethod
    def post_message(thread_id: int, sender_id: int, body: str) -> Message:
        conn = get_connection()
        cursor = conn.execute(
            'INSERT INTO messages (thread_id, sender_id, body) VALUES (?, ?, ?)',
            (thread_id, sender_id, body)
        )
        conn.execute('UPDATE message_threads SET updated_at = CURRENT_TIMESTAMP WHERE thread_id = ?', (thread_id,))
        conn.commit()
        return MessageDAL.get_message_by_id(cursor.lastrowid)

    @staticmethod
    def get_message_by_id(message_id: int) -> Optional[Message]:
        conn = get_connection()
        row = conn.execute('SELECT * FROM messages WHERE message_id = ?', (message_id,)).fetchone()
        return MessageDAL._message_row(row)

    @staticmethod
    def get_messages_for_thread(thread_id: int, limit: int = 50) -> List[Message]:
        conn = get_connection()
        rows = conn.execute(
            'SELECT * FROM messages WHERE thread_id = ? ORDER BY created_at ASC LIMIT ?',
            (thread_id, limit)
        ).fetchall()
        return [MessageDAL._message_row(row) for row in rows]
