"""Task 业务逻辑层"""
from backend.models.task import Task
from backend.repositories.local_task_repo import LocalTaskRepo


class TaskService:
    """任务服务：校验 + 仓储调用"""

    def __init__(self):
        self.repo = LocalTaskRepo()

    def get_all(self, owner_id: str | None = None) -> list[dict]:
        return [t.to_frontend() for t in self.repo.list_all(owner_id)]

    def get_guest_count(self) -> int:
        return len(self.repo.list_guest())

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

    def bind_guest_tasks(self, owner_id: str) -> int:
        """将游客任务绑定到用户，返回绑定数量"""
        return self.repo.bind_guest_to_user(owner_id)

    def unbind_user_tasks(self, owner_id: str) -> int:
        """将用户任务解绑为游客任务，返回解绑数量"""
        return self.repo.unbind_user_tasks(owner_id)
