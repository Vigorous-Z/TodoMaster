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

    def list_all(self, owner_id: str | None = None) -> list[Task]:
        """None = 游客任务（user_id IS NULL），传值 = 指定用户任务"""
        conn = get_connection()
        if owner_id is not None:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE deleted_at IS NULL AND user_id = ? ORDER BY sort_order, created_at DESC",
                (owner_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE deleted_at IS NULL AND user_id IS NULL ORDER BY sort_order, created_at DESC"
            ).fetchall()
        conn.close()
        return [Task.from_row(dict(r)) for r in rows]

    def list_guest(self) -> list[Task]:
        """游客任务（user_id IS NULL）"""
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM tasks WHERE deleted_at IS NULL AND user_id IS NULL ORDER BY sort_order, created_at DESC"
        ).fetchall()
        conn.close()
        return [Task.from_row(dict(r)) for r in rows]

    def bind_guest_to_user(self, user_id: str) -> int:
        """将游客任务绑定到指定用户，返回绑定数量"""
        conn = get_connection()
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        c = conn.execute(
            "UPDATE tasks SET user_id = ?, updated_at = ? WHERE deleted_at IS NULL AND user_id IS NULL",
            (user_id, now),
        )
        count = c.rowcount
        conn.commit()
        conn.close()
        return count

    def unbind_user_tasks(self, user_id: str) -> int:
        """将用户任务解绑为游客任务，返回解绑数量"""
        conn = get_connection()
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        c = conn.execute(
            "UPDATE tasks SET user_id = NULL, updated_at = ? WHERE deleted_at IS NULL AND user_id = ?",
            (now, user_id),
        )
        count = c.rowcount
        conn.commit()
        conn.close()
        return count

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
