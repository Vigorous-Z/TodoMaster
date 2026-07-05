"""SQLite 数据库连接管理与建表"""
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def get_db_path():
    """获取数据库文件路径，位于项目根目录下的 data/ 目录"""
    # backend/core/database.py → core → backend → 项目根目录
    project_root = Path(__file__).resolve().parent.parent.parent
    db_dir = project_root / "data"
    db_dir.mkdir(parents=True, exist_ok=True)
    return str(db_dir / "data.db")


def get_connection():
    """获取 SQLite 连接，开启 WAL 模式和外键"""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """首次启动建表"""
    conn = get_connection()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS tasks (
        uuid        TEXT PRIMARY KEY,
        version     INTEGER NOT NULL DEFAULT 1,
        title       TEXT NOT NULL,
        description TEXT,
        due_date    TEXT,
        priority    TEXT DEFAULT 'medium',
        status      TEXT DEFAULT 'active',
        project     TEXT DEFAULT 'inbox',
        tags        TEXT DEFAULT '[]',
        created_at  TEXT NOT NULL,
        updated_at  TEXT NOT NULL,
        synced_at   TEXT,
        deleted_at  TEXT,
        parent_uuid TEXT,
        sort_order  INTEGER DEFAULT 0,
        extras      TEXT DEFAULT '{}',
        user_id     TEXT
    );

    CREATE TABLE IF NOT EXISTS chat_sessions (
        session_id  TEXT PRIMARY KEY,
        user_id     TEXT,
        title       TEXT,
        messages    TEXT NOT NULL DEFAULT '[]',
        is_starred  INTEGER DEFAULT 0,
        created_at  TEXT NOT NULL,
        updated_at  TEXT NOT NULL,
        deleted_at  TEXT
    );

    CREATE TABLE IF NOT EXISTS local_users (
        user_id     TEXT PRIMARY KEY,
        prefix      TEXT NOT NULL,
        suffix      INTEGER NOT NULL,
        password_hash TEXT NOT NULL,
        created_at  TEXT NOT NULL
    );
    """)
    conn.commit()

    # 首次启动写入种子数据
    cursor = conn.execute("SELECT COUNT(*) FROM tasks")
    if cursor.fetchone()[0] == 0:
        _seed_tasks(conn)
    conn.close()


# ====== 种子数据 ======

SEED_TASKS = [
    # (uuid, title, due_date, priority, status, project, tags, created_at, updated_at)
    ("a0000001-0000-0000-0000-000000000001", "给导师发邮件汇报本周进度", "2026-07-02T15:00:00", "high", "active", "work", json.dumps(["工作"], ensure_ascii=False)),
    ("a0000002-0000-0000-0000-000000000002", "项目进度讨论会议", "2026-07-02T09:00:00", "high", "completed", "work", json.dumps(["工作", "会议"], ensure_ascii=False)),
    ("a0000003-0000-0000-0000-000000000003", "完成季度报告并提交审核", "2026-07-03T23:59:00", "high", "active", "work", json.dumps(["工作"], ensure_ascii=False)),
    ("a0000004-0000-0000-0000-000000000004", "预约财务对账时间", "2026-07-04T12:00:00", "medium", "active", "work", json.dumps(["工作"], ensure_ascii=False)),
    ("a0000005-0000-0000-0000-000000000005", "查阅 NLP 相关文献并做笔记", "2026-07-05T18:00:00", "low", "active", "learn", json.dumps(["学习"], ensure_ascii=False)),
    ("a0000006-0000-0000-0000-000000000006", "更新项目 README 和技术文档", "2026-07-03T17:00:00", "medium", "active", "work", json.dumps(["工作"], ensure_ascii=False)),
    ("a0000007-0000-0000-0000-000000000007", "跑步 5 公里", "2026-07-02T07:00:00", "medium", "completed", "personal", json.dumps(["个人"], ensure_ascii=False)),
    ("a0000008-0000-0000-0000-000000000008", "整理桌面和下载文件夹", "2026-07-06T12:00:00", "low", "active", "personal", json.dumps(["个人"], ensure_ascii=False)),
]

SQL_INSERT_SEED = """INSERT INTO tasks (uuid, title, due_date, priority, status, project, tags, created_at, updated_at)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""


def _seed_tasks(conn: sqlite3.Connection) -> None:
    """写入种子数据到已打开的连接"""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rows = [row + (now, now) for row in SEED_TASKS]
    conn.executemany(SQL_INSERT_SEED, rows)
    conn.commit()


def seed_reset() -> int:
    """清空 tasks 表并重新注入种子数据，返回写入条数"""
    conn = get_connection()
    conn.execute("DELETE FROM tasks")
    _seed_tasks(conn)
    count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    conn.close()
    return count
