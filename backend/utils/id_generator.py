"""UUID 生成器"""
import uuid


def new_uuid() -> str:
    return str(uuid.uuid4())