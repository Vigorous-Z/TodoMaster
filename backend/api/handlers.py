"""PyWebView 暴露给前端的 API 函数"""
from backend.services.task_service import TaskService
from backend.services import user_service

_task_service = TaskService()

# ---- 任务 API ----

def api_get_tasks(data: dict = None) -> list[dict]:
    owner_id = data.get("owner_id") if data else None
    return _task_service.get_all(owner_id)

def api_add_task(data: dict) -> dict:
    return _task_service.add(data)

def api_update_task(task_uuid: str, data: dict) -> dict:
    return _task_service.update(task_uuid, data)

def api_delete_task(task_uuid: str) -> dict:
    _task_service.delete(task_uuid)
    return {"success": True}

def api_toggle_task(task_uuid: str) -> dict:
    return _task_service.toggle(task_uuid)

# ---- 用户 API ----

def api_register(data: dict) -> dict:
    return user_service.register(data["prefix"], data["password"])

def api_login(data: dict) -> dict:
    return user_service.login(data["user_id"], data["password"])

def api_get_current_user(data: dict) -> dict | None:
    return user_service.get_user(data["user_id"])

def api_logout(data: dict) -> dict:
    return {"success": True}

def api_get_guest_task_count(data: dict) -> int:
    return _task_service.get_guest_count()

def api_bind_guest_tasks(data: dict) -> dict:
    count = _task_service.bind_guest_tasks(data["owner_id"])
    return {"success": True, "count": count}

def api_unbind_user_tasks(data: dict) -> dict:
    count = _task_service.unbind_user_tasks(data["owner_id"])
    return {"success": True, "count": count}


# ---- 云端同步 API ----
from backend.cloud.supabase_sync import (
    sync_all,
    push_tasks, pull_tasks,
    push_user, pull_user, find_user_in_cloud,
)


def api_cloud_sync(data: dict) -> dict:
    """全量推拉：推送本地全部数据到云端，再拉回云端数据覆盖本地"""
    user_id = data.get("user_id", "")
    if not user_id:
        return {"success": False, "error": "请先登录"}
    return {"success": True, **sync_all(user_id)}


def api_cloud_push(data: dict) -> dict:
    """仅上传任务"""
    user_id = data.get("user_id", "")
    if not user_id:
        return {"success": False, "error": "请先登录"}
    count = push_tasks(user_id)
    return {"success": True, "count": count}


def api_cloud_pull(data: dict) -> dict:
    """仅下载任务"""
    user_id = data.get("user_id", "")
    if not user_id:
        return {"success": False, "error": "请先登录"}
    count = pull_tasks(user_id)
    return {"success": True, "count": count}


def api_find_user_in_cloud(data: dict) -> dict:
    """云端查找用户，找到后拉到本地（用于跨设备登录）"""
    user_id = data.get("user_id", "")
    if not user_id:
        return {"success": False, "error": "缺少 user_id"}
    result = find_user_in_cloud(user_id)
    if result:
        return {"success": True, "found": True, "user": {"user_id": result["user_id"], "prefix": result["prefix"], "created_at": result["created_at"]}}
    return {"success": True, "found": False}


# ---- AI 解析 API ----
from backend.services.ai_service import parse as ai_parse, parse_with_thinking


def api_ai_parse(data: dict) -> dict:
    """自然语言 → 结构化日程解析（快速模式）"""
    text = data.get("text", "")
    if not text.strip():
        return {"error": "输入为空"}
    return ai_parse(text.strip())


def api_ai_parse_thinking(data: dict) -> dict:
    """自然语言 → 结构化日程解析（MCP 多步推理模式）"""
    text = data.get("text", "")
    if not text.strip():
        return {"error": "输入为空"}
    result = parse_with_thinking(text.strip())
    # MCP 推理结果附上使用的模式标识
    if "error" not in result:
        result["mode"] = "mcp-sequential-thinking"
    return result
