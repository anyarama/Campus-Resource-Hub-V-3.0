"""Review data helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from src.data_access.db import get_connection


@dataclass
class Review:
    review_id: int
    resource_id: int
    reviewer_id: int
    rating: int
    comment: str | None
    created_at: str


class ReviewDAL:
    @staticmethod
    def _row(row) -> Optional[Review]:
        if not row:
            return None
        return Review(
            review_id=row['review_id'],
            resource_id=row['resource_id'],
            reviewer_id=row['reviewer_id'],
            rating=row['rating'],
            comment=row['comment'],
            created_at=row['created_at'],
        )

    @staticmethod
    def create_review(resource_id: int, reviewer_id: int, rating: int, comment: str | None):
        conn = get_connection()
        cursor = conn.execute(
            'INSERT INTO reviews (resource_id, reviewer_id, rating, comment) VALUES (?, ?, ?, ?)',
            (resource_id, reviewer_id, rating, comment)
        )
        conn.commit()
        return ReviewDAL.get_review_by_id(cursor.lastrowid)

    @staticmethod
    def get_review_by_id(review_id: int) -> Optional[Review]:
        conn = get_connection()
        row = conn.execute('SELECT * FROM reviews WHERE review_id = ?', (review_id,)).fetchone()
        return ReviewDAL._row(row)

    @staticmethod
    def list_for_resource(resource_id: int) -> List[Review]:
        conn = get_connection()
        rows = conn.execute('SELECT * FROM reviews WHERE resource_id = ? ORDER BY created_at DESC', (resource_id,)).fetchall()
        return [ReviewDAL._row(row) for row in rows]

    @staticmethod
    def list_recent(limit: int = 10) -> List[Review]:
        conn = get_connection()
        rows = conn.execute('SELECT * FROM reviews ORDER BY created_at DESC LIMIT ?', (limit,)).fetchall()
        return [ReviewDAL._row(row) for row in rows]

    @staticmethod
    def user_has_reviewed(resource_id: int, reviewer_id: int) -> bool:
        conn = get_connection()
        row = conn.execute(
            'SELECT 1 FROM reviews WHERE resource_id = ? AND reviewer_id = ? LIMIT 1',
            (resource_id, reviewer_id)
        ).fetchone()
        return bool(row)

    @staticmethod
    def delete_review(review_id: int):
        conn = get_connection()
        conn.execute('DELETE FROM reviews WHERE review_id = ?', (review_id,))
        conn.commit()

    @staticmethod
    def get_average_for_resource(resource_id: int) -> dict:
        conn = get_connection()
        row = conn.execute(
            'SELECT AVG(rating) AS avg_rating, COUNT(*) AS total_reviews FROM reviews WHERE resource_id = ?',
            (resource_id,)
        ).fetchone()
        return {
            'avg_rating': row['avg_rating'] or 0,
            'total_reviews': row['total_reviews'] or 0,
        }
