"""Task 本地 SQLite 仓储"""
import json
from datetime import datetime, timezone

from backend.core.database import get_connection
from backend.models.task import Task


class LocalTaskRepo:
    """本地任务 CRUD"""

    def add(self, task: Task) -> Task:
        conn = get_connection()
        row = task.to_row()
        cols = ", ".join(row.keys())
        placeholders = ", ".join(["?"] * len(row))
        conn.execute(f"INSERT INTO tasks ({cols}) VALUES ({placeholders})", list(row.values()))
        conn.commit()
        conn.close()
        return task

    def get(self, task_uuid: str) -> Task | None:
        conn = get_connection()
        row = conn.execute(
            "SELECT * FROM tasks WHERE uuid = ? AND deleted_at IS NULL", (task_uuid,)
        ).fetchone()
        conn.close()
        return Task.from_row(dict(row)) if row else None

    def list_all(self) -> list[Task]:
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM tasks WHERE deleted_at IS NULL ORDER BY sort_order, created_at DESC"
        ).fetchall()
        conn.close()
        return [Task.from_row(dict(r)) for r in rows]

    def update(self, task: Task) -> Task:
        task.version += 1
        task.updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        row = task.to_row()
        set_clause = ", ".join(f"{k} = ?" for k in row)
        conn = get_connection()
        conn.execute(f"UPDATE tasks SET {set_clause} WHERE uuid = ?", list(row.values()) + [task.uuid])
        conn.commit()
        conn.close()
        return task

    def soft_delete(self, task_uuid: str) -> None:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        conn = get_connection()
        conn.execute("UPDATE tasks SET deleted_at = ?, updated_at = ? WHERE uuid = ?", (now, now, task_uuid))
        conn.commit()
        conn.close()