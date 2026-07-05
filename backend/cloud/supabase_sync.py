"""Supabase 云端同步模块。全量推拉，以云端为准。离线时自动降级，不阻塞本地操作。"""
import json
import os
import socket

from backend.core.database import get_connection
from backend.models.task import Task
from backend.repositories.local_task_repo import LocalTaskRepo

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://galiyyrwmrhgloolbnjy.supabase.co")
SUPABASE_SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdhbGl5eXJ3bXJoZ2xvb2xibmp5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MzI0MzIwNCwiZXhwIjoyMDk4ODE5MjA0fQ.fAOuW0gHvB8NkIBWKOc1_p8lzdFeYt6UK_dvneSjGZg")

_repo = LocalTaskRepo()


def _is_online() -> bool:
    """检查云端是否可达（3 秒超时），离线时返回 False"""
    try:
        host = SUPABASE_URL.replace("https://", "").replace("http://", "").rstrip("/")
        s = socket.create_connection((host, 443), timeout=3)
        s.close()
        return True
    except Exception:
        return False


def _get_client():
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


# ========== Tasks ==========

def push_tasks(user_id: str) -> int:
    if not _is_online():
        return 0
    supabase = _get_client()
    tasks = _repo.list_all(user_id if user_id else None)
    rows = [_task_to_cloud(t, user_id) for t in tasks]
    supabase.table("tasks").delete().eq("user_id", user_id).execute()
    if rows:
        supabase.table("tasks").insert(rows).execute()
    return len(rows)


def pull_tasks(user_id: str) -> int:
    if not _is_online():
        return 0
    supabase = _get_client()
    resp = supabase.table("tasks").select("*").eq("user_id", user_id).execute()
    rows = resp.data or []
    _repo.wipe_all(user_id if user_id else None)
    tasks = []
    for r in rows:
        try:
            tasks.append(_cloud_row_to_task(r))
        except Exception as e:
            print(f"[cloud pull tasks] 跳过异常行: {e}")
    _repo.add_bulk(tasks)
    return len(tasks)


# ========== Users ==========

def push_user(user_id: str) -> bool:
    """上传单个用户到云端"""
    if not _is_online():
        return False
    conn = get_connection()
    row = conn.execute("SELECT * FROM local_users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    if not row:
        return False
    supabase = _get_client()
    data = dict(row)
    supabase.table("local_users").upsert(data, on_conflict="user_id").execute()
    return True


def pull_user(user_id: str) -> dict | None:
    """从云端拉取单个用户到本地，返回用户数据或 None"""
    if not _is_online():
        return None
    supabase = _get_client()
    resp = supabase.table("local_users").select("*").eq("user_id", user_id).execute()
    rows = resp.data or []
    if not rows:
        return None
    data = dict(rows[0])
    conn = get_connection()
    conn.execute(
        """INSERT OR REPLACE INTO local_users (user_id, prefix, suffix, password_hash, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        (data["user_id"], data["prefix"], data["suffix"], data["password_hash"], data["created_at"]),
    )
    conn.commit()
    conn.close()
    return data


def find_user_in_cloud(user_id: str) -> dict | None:
    """云端查找用户，找到后自动拉到本地"""
    return pull_user(user_id)


# ========== Chat Sessions ==========

def push_chats(user_id: str) -> int:
    if not _is_online():
        return 0
    supabase = _get_client()
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM chat_sessions WHERE user_id = ? AND deleted_at IS NULL", (user_id,)
    ).fetchall()
    conn.close()
    rows_data = [_chat_to_cloud(dict(r)) for r in rows]
    supabase.table("chat_sessions").delete().eq("user_id", user_id).execute()
    if rows_data:
        supabase.table("chat_sessions").insert(rows_data).execute()
    return len(rows_data)


def pull_chats(user_id: str) -> int:
    if not _is_online():
        return 0
    supabase = _get_client()
    resp = supabase.table("chat_sessions").select("*").eq("user_id", user_id).execute()
    rows = resp.data or []
    conn = get_connection()
    conn.execute("DELETE FROM chat_sessions WHERE user_id = ?", (user_id,))
    for r in rows:
        data = _chat_from_cloud(r)
        cols = ", ".join(data.keys())
        ph = ", ".join(["?"] * len(data))
        conn.execute(f"INSERT INTO chat_sessions ({cols}) VALUES ({ph})", list(data.values()))
    conn.commit()
    conn.close()
    return len(rows)


# ========== 全量同步 ==========

def sync_all(user_id: str) -> dict:
    """全量推拉三张表：先推本地上云端，再从云端拉回覆盖本地"""
    user_push = push_user(user_id)
    tasks_push = push_tasks(user_id)
    chats_push = push_chats(user_id)

    user_pull = pull_user(user_id)
    tasks_pull = pull_tasks(user_id)
    chats_pull = pull_chats(user_id)

    return {
        "push": {"user": user_push, "tasks": tasks_push, "chats": chats_push},
        "pull": {"user": user_pull is not None, "tasks": tasks_pull, "chats": chats_pull},
        "total": tasks_pull,
    }


# ========== 辅助函数 ==========

def _chat_to_cloud(row: dict) -> dict:
    from datetime import datetime, timezone
    # 确保 messages 是 JSONB 兼容的 list/dict
    if isinstance(row.get("messages"), str):
        row["messages"] = json.loads(row["messages"])
    return row


def _chat_from_cloud(row: dict) -> dict:
    row = dict(row)
    if not isinstance(row.get("messages"), str):
        row["messages"] = json.dumps(row["messages"], ensure_ascii=False)
    return row


def _task_to_cloud(t: Task, user_id: str) -> dict:
    row = t.to_row()
    row["user_id"] = user_id or None
    if "tags" in row and isinstance(row["tags"], str):
        row["tags"] = json.loads(row["tags"])
    if "extras" in row and isinstance(row["extras"], str):
        row["extras"] = json.loads(row["extras"])
    return row


def _cloud_row_to_task(row: dict) -> Task:
    row = dict(row)
    if "tags" in row and not isinstance(row["tags"], str):
        row["tags"] = json.dumps(row["tags"], ensure_ascii=False)
    if "extras" in row and not isinstance(row["extras"], str):
        row["extras"] = json.dumps(row["extras"], ensure_ascii=False)
    return Task.from_row(row)
