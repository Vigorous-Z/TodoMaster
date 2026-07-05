"""Task 数据模型 —— Pydantic v2"""
import json
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

from ..utils.id_generator import new_uuid


class Task(BaseModel):
    """日程任务模型"""
    uuid: str = Field(default_factory=new_uuid)
    version: int = 1
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: str = "medium"
    status: str = "active"
    project: str = "inbox"
    tags: list[str] = []
    created_at: str = ""
    updated_at: str = ""
    synced_at: Optional[str] = None
    deleted_at: Optional[str] = None
    parent_uuid: Optional[str] = None
    sort_order: int = 0
    extras: dict = {}
    user_id: Optional[str] = None

    def model_post_init(self, _ctx):
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    def to_row(self) -> dict:
        data = self.model_dump()
        data["tags"] = json.dumps(data["tags"], ensure_ascii=False)
        data["extras"] = json.dumps(data["extras"], ensure_ascii=False)
        return data

    @classmethod
    def from_row(cls, row: dict) -> "Task":
        row = dict(row)
        row["tags"] = json.loads(row.get("tags", "[]"))
        row["extras"] = json.loads(row.get("extras", "{}"))
        return cls(**row)

    def _format_due(self) -> Optional[str]:
        """ISO -> 前端兼容格式 'YYYY-MM-DD HH:MM'"""
        if not self.due_date:
            return None
        return self.due_date.replace("T", " ")[:16]

    def to_frontend(self) -> dict:
        return {
            "id": self.uuid,
            "title": self.title,
            "description": self.description,
            "due": self._format_due(),
            "priority": self.priority,
            "status": self.status,
            "project": self.project,
            "tags": self.tags,
            "done": self.status == "completed",
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }