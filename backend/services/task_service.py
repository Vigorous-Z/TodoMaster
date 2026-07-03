"""Task 业务逻辑层"""
from backend.models.task import Task
from backend.repositories.local_task_repo import LocalTaskRepo


class TaskService:
    """任务服务：校验 + 仓储调用"""

    def __init__(self):
        self.repo = LocalTaskRepo()

    def get_all(self) -> list[dict]:
        return [t.to_frontend() for t in self.repo.list_all()]

    def add(self, data: dict) -> dict:
        task = Task(**data)
        self.repo.add(task)
        return task.to_frontend()

    def update(self, task_uuid: str, data: dict) -> dict:
        existing = self.repo.get(task_uuid)
        if not existing:
            raise ValueError(f"任务不存在: {task_uuid}")
        for k, v in data.items():
            if hasattr(existing, k):
                setattr(existing, k, v)
        self.repo.update(existing)
        return existing.to_frontend()

    def delete(self, task_uuid: str) -> None:
        self.repo.soft_delete(task_uuid)

    def toggle(self, task_uuid: str) -> dict:
        existing = self.repo.get(task_uuid)
        if not existing:
            raise ValueError(f"任务不存在: {task_uuid}")
        existing.status = "active" if existing.status == "completed" else "completed"
        self.repo.update(existing)
        return existing.to_frontend()