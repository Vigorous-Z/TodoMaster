"""PyWebView 暴露给前端的 API 函数"""
from backend.services.task_service import TaskService

_task_service = TaskService()


def api_get_tasks() -> list[dict]:
    return _task_service.get_all()


def api_add_task(data: dict) -> dict:
    return _task_service.add(data)


def api_update_task(task_uuid: str, data: dict) -> dict:
    return _task_service.update(task_uuid, data)


def api_delete_task(task_uuid: str) -> dict:
    _task_service.delete(task_uuid)
    return {"success": True}


def api_toggle_task(task_uuid: str) -> dict:
    return _task_service.toggle(task_uuid)