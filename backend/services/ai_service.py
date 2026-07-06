"""AI 自然语言解析服务 —— LangChain + DeepSeek"""
import json
import os
import re
from datetime import datetime, timezone

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
MAX_RETRIES = 3

SYSTEM_PROMPT = """你是一个日程解析助手。根据用户的自然语言输入，提取结构化日程信息。

当前时间：{now}

规则：
1. 提取标题（title）：简短概括任务内容
2. 推断截止时间（due_date）：格式 YYYY-MM-DD HH:MM:SS，根据"后天""下周""三天后"等相对时间结合当前时间推算
3. 判断优先级（priority）：high / medium / low，紧急或带"务必""尽快"等字眼用 high
4. 提取标签（tags）：根据内容匹配，可选：工作、个人、学习、会议、健康、财务
5. 提取描述（description）：任务补充细节，没有则为空字符串
6. 提取项目（project）：work / personal / learn，默认 personal
7. 如果输入无法识别为有效任务，返回 {{"error": "无法识别"}}

只返回 JSON，不要任何额外文字。格式：
{{"title":"...","due_date":"...","priority":"...","tags":[...],"description":"...","project":"..."}}"""


def _get_llm():
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model="deepseek-chat",
        api_key=DEEPSEEK_API_KEY,
        base_url=DEEPSEEK_BASE_URL,
        temperature=0.1,
        timeout=15,
    )


def parse(text: str) -> dict:
    """解析自然语言 → 结构化日程，失败返回含 error 的 dict"""
    if not DEEPSEEK_API_KEY:
        return {"error": "未配置 DEEPSEEK_API_KEY"}

    now = datetime.now().strftime("%Y年%m月%d日 %H:%M")
    prompt = SYSTEM_PROMPT.format(now=now)

    llm = _get_llm()

    for attempt in range(MAX_RETRIES):
        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            response = llm.invoke([
                SystemMessage(content=prompt),
                HumanMessage(content=text),
            ])
            raw = response.content.strip()
            # 提取 JSON（去掉可能的 markdown 代码块包裹）
            match = re.search(r"\{[\s\S]*\}", raw)
            if not match:
                raise ValueError(f"AI 未返回 JSON: {raw[:200]}")
            data = json.loads(match.group())
            # 校验
            validated = _validate(data)
            return validated
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                # 带错误反馈重试
                prompt = SYSTEM_PROMPT.format(now=now) + f"\n\n上次解析错误：{e}，请修正后重新输出 JSON。"
            else:
                return {"error": f"AI 解析失败（已重试{MAX_RETRIES}次）: {e}"}

    return {"error": "未知错误"}


def _validate(data: dict) -> dict:
    """校验并补全 AI 返回的数据"""
    if "error" in data:
        return data
    if "title" not in data or not data["title"]:
        raise ValueError("缺少 title 字段")

    result = {
        "title": data["title"].strip(),
        "due_date": _normalize_due(data.get("due_date", "")),
        "priority": data.get("priority", "medium"),
        "tags": data.get("tags", []),
        "description": data.get("description", ""),
        "project": data.get("project", "personal"),
    }

    if result["priority"] not in ("high", "medium", "low"):
        result["priority"] = "medium"
    if not isinstance(result["tags"], list):
        result["tags"] = []
    result["tags"] = [t for t in result["tags"] if isinstance(t, str)]

    return result


def _normalize_due(due: str) -> str:
    """标准化日期格式 YYYY-MM-DD HH:MM:SS"""
    if not due:
        tomorrow = datetime.now().replace(hour=23, minute=59, second=0, microsecond=0)
        return tomorrow.strftime("%Y-%m-%d %H:%M:%S")
    due = due.strip().replace("T", " ")
    if len(due) == 10:  # YYYY-MM-DD
        due += " 23:59:00"
    elif len(due) == 16:  # YYYY-MM-DD HH:MM
        due += ":00"
    return due
