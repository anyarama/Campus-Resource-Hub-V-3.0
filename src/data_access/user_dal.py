"""Data access helpers for users."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from src.data_access.db import get_connection


@dataclass
class User(UserMixin):
    user_id: int
    name: str
    email: str
    role: str
    department: str | None
    email_verified: int

    def get_id(self) -> str:
        return str(self.user_id)


class UserDAL:
    @staticmethod
    def _row_to_user(row) -> Optional[User]:
        if row is None:
            return None
        return User(
            user_id=row['user_id'],
            name=row['name'],
            email=row['email'],
            role=row['role'],
            department=row['department'],
            email_verified=row['email_verified'],
        )

    @staticmethod
    def create_user(name: str, email: str, password: str, role: str = 'student', department: str | None = None):
        password_hash = generate_password_hash(password)
        conn = get_connection()
        cursor = conn.execute(
            'INSERT INTO users (name, email, password_hash, role, department, email_verified) VALUES (?, ?, ?, ?, ?, ?)',
            (name, email, password_hash, role, department, 1 if role == 'admin' else 0)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return UserDAL.get_user_by_id(user_id)

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        conn = get_connection()
        row = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        return UserDAL._row_to_user(row)

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        conn = get_connection()
        row = conn.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)).fetchone()
        return UserDAL._row_to_user(row)

    @staticmethod
    def verify_password(email: str, password: str) -> Optional[User]:
        conn = get_connection()
        row = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        if row and check_password_hash(row['password_hash'], password):
            return UserDAL._row_to_user(row)
        return None

    @staticmethod
    def list_users():
        conn = get_connection()
        rows = conn.execute('SELECT * FROM users ORDER BY created_at DESC').fetchall()
        return [UserDAL._row_to_user(row) for row in rows]
