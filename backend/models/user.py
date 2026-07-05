"""用户数据模型"""
from pydantic import BaseModel, Field


class LocalUser(BaseModel):
    user_id: str  # 如 "张三#12345"
    prefix: str
    suffix: int
    password_hash: str
    created_at: str = ""

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "prefix": self.prefix,
            "created_at": self.created_at,
        }