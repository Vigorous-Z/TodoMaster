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
