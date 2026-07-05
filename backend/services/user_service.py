"""用户业务逻辑层"""
import hashlib
import secrets
from datetime import datetime, timezone

from backend.core.database import get_connection
from backend.models.user import LocalUser


def _hash_password(password: str) -> str:
    """简单哈希（用 hashlib 替代 bcrypt，零依赖）"""
    salt = secrets.token_hex(8)
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{h}"


def _check_password(password: str, password_hash: str) -> bool:
    salt, expected = password_hash.split(":", 1)
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    return h == expected


def _generate_suffix() -> int:
    """随机5位不重复数字（10000-99999）"""
    import random
    conn = get_connection()
    existing = {r[0] for r in conn.execute("SELECT suffix FROM local_users").fetchall()}
    conn.close()
    for _ in range(100):
        s = random.randint(10000, 99999)
        if s not in existing:
            return s
    return random.randint(10000, 99999)


def register(prefix: str, password: str) -> dict:
    if len(password) < 4:
        raise ValueError("密码至少4位")
    suffix = _generate_suffix()
    user_id = f"{prefix}#{suffix}"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    pwd_hash = _hash_password(password)
    conn = get_connection()
    conn.execute(
        "INSERT INTO local_users (user_id, prefix, suffix, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, prefix, suffix, pwd_hash, now),
    )
    conn.commit()
    conn.close()
    # 生成 token
    token = secrets.token_urlsafe(32)
    # 同步到云端
    try:
        from backend.cloud.supabase_sync import push_user
        push_user(user_id)
    except Exception:
        pass
    return {"user": {"user_id": user_id, "prefix": prefix, "created_at": now}, "token": token}


def login(user_id: str, password: str) -> dict:
    conn = get_connection()
    row = conn.execute("SELECT * FROM local_users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()

    # 本地没找到，尝试从云端拉取
    if not row:
        from backend.cloud.supabase_sync import find_user_in_cloud
        cloud_user = find_user_in_cloud(user_id)
        if not cloud_user:
            raise ValueError("用户不存在")
        row = cloud_user

    if not _check_password(password, row["password_hash"]):
        raise ValueError("密码错误")
    token = secrets.token_urlsafe(32)
    # 登录成功，同步用户到云端（确保云端也有此用户）
    try:
        from backend.cloud.supabase_sync import push_user
        push_user(row["user_id"])
    except Exception:
        pass
    return {
        "user": {"user_id": row["user_id"], "prefix": row["prefix"], "created_at": row["created_at"]},
        "token": token,
    }


def get_user(user_id: str) -> dict | None:
    conn = get_connection()
    row = conn.execute("SELECT * FROM local_users WHERE user_id = ?", (user_id,)).fetchone()
    conn.close()
    if not row:
        return None
    return {"user_id": row["user_id"], "prefix": row["prefix"], "created_at": row["created_at"]}