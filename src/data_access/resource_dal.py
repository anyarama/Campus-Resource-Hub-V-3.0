"""Data access helpers for resources."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from src.data_access.db import get_connection


@dataclass
class Resource:
    resource_id: int
    owner_id: int
    title: str
    summary: str
    category: str
    location: str
    capacity: int
    availability_notes: str | None
    status: str
    gallery: List[str]


class ResourceDAL:
    @staticmethod
    def _row_to_resource(row) -> Optional[Resource]:
        if row is None:
            return None
        gallery_rows = ResourceDAL._fetch_gallery(row['resource_id'])
        return Resource(
            resource_id=row['resource_id'],
            owner_id=row['owner_id'],
            title=row['title'],
            summary=row['summary'],
            category=row['category'],
            location=row['location'],
            capacity=row['capacity'],
            availability_notes=row['availability_notes'],
            status=row['status'],
            gallery=gallery_rows,
        )

    @staticmethod
    def _fetch_gallery(resource_id: int) -> List[str]:
        conn = get_connection()
        rows = conn.execute(
            'SELECT file_path FROM resource_images WHERE resource_id = ? ORDER BY image_id ASC',
            (resource_id,)
        ).fetchall()
        return [row['file_path'] for row in rows]

    @staticmethod
    def create_resource(owner_id: int, title: str, summary: str, category: str, location: str,
                        capacity: int, availability_notes: str | None, status: str, gallery: List[str]):
        conn = get_connection()
        cursor = conn.execute(
            '''INSERT INTO resources (owner_id, title, summary, category, location, capacity, availability_notes, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (owner_id, title, summary, category, location, capacity, availability_notes, status)
        )
        resource_id = cursor.lastrowid
        for path in gallery:
            conn.execute(
                'INSERT INTO resource_images (resource_id, file_path) VALUES (?, ?)',
                (resource_id, path)
            )
        conn.commit()
        return ResourceDAL.get_resource_by_id(resource_id)

    @staticmethod
    def update_resource(resource_id: int, **fields):
        conn = get_connection()
        gallery = fields.pop('gallery', None)
        if fields:
            clauses = []
            params: List[object] = []
            for key, value in fields.items():
                clauses.append(f"{key} = ?")
                params.append(value)
            params.append(resource_id)
            conn.execute(
                f"UPDATE resources SET {', '.join(clauses)}, updated_at = CURRENT_TIMESTAMP WHERE resource_id = ?",
                params
            )
        if gallery is not None:
            conn.execute('DELETE FROM resource_images WHERE resource_id = ?', (resource_id,))
            for path in gallery:
                conn.execute('INSERT INTO resource_images (resource_id, file_path) VALUES (?, ?)', (resource_id, path))
        conn.commit()

    @staticmethod
    def get_resource_by_id(resource_id: int) -> Optional[Resource]:
        conn = get_connection()
        row = conn.execute('SELECT * FROM resources WHERE resource_id = ?', (resource_id,)).fetchone()
        return ResourceDAL._row_to_resource(row)

    @staticmethod
    def get_resources_by_owner(owner_id: int) -> List[Resource]:
        conn = get_connection()
        rows = conn.execute(
            'SELECT * FROM resources WHERE owner_id = ? ORDER BY created_at DESC',
            (owner_id,)
        ).fetchall()
        return [ResourceDAL._row_to_resource(row) for row in rows]

    @staticmethod
    def search_resources(keyword=None, category=None, location=None, min_capacity=None, status='published') -> List[Resource]:
        clauses = []
        params: List[object] = []
        if status:
            clauses.append('status = ?')
            params.append(status)
        if keyword:
            clauses.append('(title LIKE ? OR summary LIKE ?)')
            params.extend([f'%{keyword}%', f'%{keyword}%'])
        if category:
            clauses.append('category = ?')
            params.append(category)
        if location:
            clauses.append('location LIKE ?')
            params.append(f'%{location}%')
        if min_capacity is not None:
            clauses.append('capacity >= ?')
            params.append(min_capacity)
        where = ' AND '.join(clauses) if clauses else '1=1'
        query = f'SELECT * FROM resources WHERE {where} ORDER BY created_at DESC'
        conn = get_connection()
        rows = conn.execute(query, tuple(params)).fetchall()
        return [ResourceDAL._row_to_resource(row) for row in rows]

    @staticmethod
    def get_featured_resources(limit: int = 4) -> List[Resource]:
        conn = get_connection()
        rows = conn.execute(
            'SELECT * FROM resources WHERE status = ? ORDER BY created_at DESC LIMIT ?',
            ('published', limit)
        ).fetchall()
        return [ResourceDAL._row_to_resource(row) for row in rows]

    @staticmethod
    def get_resource_stats():
        conn = get_connection()
        totals = conn.execute(
            """SELECT
                    COUNT(*) AS total,
                    SUM(CASE WHEN status = 'published' THEN 1 ELSE 0 END) AS published,
                    AVG(capacity) AS avg_capacity
                FROM resources"""
        ).fetchone()
        if not totals:
            return {'total': 0, 'published': 0, 'avg_capacity': 0}
        return {
            'total': totals['total'] or 0,
            'published': totals['published'] or 0,
            'avg_capacity': totals['avg_capacity'] or 0,
        }

    @staticmethod
    def get_related_resources(category: str, exclude_id: int, limit: int = 3) -> List[Resource]:
        conn = get_connection()
        rows = conn.execute(
            'SELECT * FROM resources WHERE category = ? AND resource_id != ? AND status = ? ORDER BY created_at DESC LIMIT ?',
            (category, exclude_id, 'published', limit)
        ).fetchall()
        return [ResourceDAL._row_to_resource(row) for row in rows]
