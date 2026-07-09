"""AI 自然语言解析服务 —— LangChain + DeepSeek + MCP Sequential Thinking"""
import json
import os
import re
from datetime import datetime, timezone

from backend.services.mcp_client import SequentialThinkingClient

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
    """解析自然语言 → 结构化日程（快速模式）"""
    if not DEEPSEEK_API_KEY:
        return {"error": "未配置 DEEPSEEK_API_KEY"}
    return _call_llm(text, SYSTEM_PROMPT)


def parse_with_thinking(text: str) -> dict:
    """基于 MCP Sequential Thinking 的多步推理解析（复杂输入模式）

    MCP 架构：
      ai_service.py ──JSON-RPC──→ mcp-sequential-thinking (MCP Server)
                                      │
                           5 阶段推理 (Problem Definition → Conclusion)

    每阶段构建一次推理步骤，最终将结构化的推理上下文注入 LLM prompt。
    """
    if not DEEPSEEK_API_KEY:
        return {"error": "未配置 DEEPSEEK_API_KEY"}

    mcp = SequentialThinkingClient()

    try:
        mcp.start()

        if not mcp._session:
            # MCP 不可用时降级为快速模式
            return parse(text)

        now = datetime.now().strftime("%Y年%m月%d日 %H:%M")

        # Stage 1 - Problem Definition
        mcp.process_thought(
            thought=f"解析用户输入的日程描述：「{text}」。当前时间：{now}。目标是将自然语言转换为结构化 JSON。",
            thought_number=1, total_thoughts=5, next_thought_needed=True,
            stage="Problem Definition",
            tags=["自然语言处理", "日程解析"],
        )

        # Stage 2 - Research（关键词和实体识别）
        keywords = _extract_keywords(text)
        time_hint = _extract_time_hint(text)
        mcp.process_thought(
            thought=f"识别关键词: {keywords}。时间线索: {time_hint or '无显式时间'}。"
                   f"需根据相对时间词汇（后天/下周/三天后）结合当前时间推算具体日期。",
            thought_number=2, total_thoughts=5, next_thought_needed=True,
            stage="Research",
            tags=["实体识别", "时间解析"],
        )

        # Stage 3 - Analysis（映射到任务字段）
        mcp.process_thought(
            thought=f"将识别出的实体映射到 Task 模型字段：title、due_date、priority(high/medium/low)、"
                   f"tags(工作/个人/学习/会议/健康/财务)、project(work/personal/learn)。"
                   f"优先根据关键词判断 urgency 级别。",
            thought_number=3, total_thoughts=5, next_thought_needed=True,
            stage="Analysis",
            tags=["字段映射", "优先级推断"],
        )

        # Stage 4 - Synthesis（构建增强 prompt + 调用 LLM）
        enhanced_prompt = SYSTEM_PROMPT + (
            f"\n\n前置推理结果："
            f"\n- 关键词：{keywords}"
            f"\n- 时间线索：{time_hint or '默认明天 23:59'}"
            f"\n- 请基于以上推理输出精确 JSON。"
        )
        mcp.process_thought(
            thought=f"合成增强 prompt 并调用 LLM 解析。Prompt 长度: {len(enhanced_prompt)} 字符。",
            thought_number=4, total_thoughts=5, next_thought_needed=True,
            stage="Synthesis",
            tags=["Prompt 构建", "LLM 调用"],
        )

        result = _call_llm(text, enhanced_prompt)
        if "error" not in result:
            result["mode"] = "mcp-sequential-thinking"

        # Stage 5 - Conclusion
        if "error" in result:
            mcp.process_thought(
                thought=f"解析失败: {result['error']}。回退到快速模式结果。",
                thought_number=5, total_thoughts=5, next_thought_needed=False,
                stage="Conclusion",
                tags=["失败", "降级"],
            )
        else:
            mcp.process_thought(
                thought=f"解析成功。输出: title={result.get('title')}, "
                       f"priority={result.get('priority')}, tags={result.get('tags')}。",
                thought_number=5, total_thoughts=5, next_thought_needed=False,
                stage="Conclusion",
                tags=["成功", "MCP 推理完成"],
            )

        # 生成推理摘要
        summary = mcp.generate_summary()
        if summary.get("success"):
            print(f"[MCP Summary] stages completed, total thoughts logged")

        return result

    except Exception as e:
        print(f"[MCP] 推理异常: {e}，降级为快速模式")
        return parse(text)
    finally:
        mcp.clear_history()
        mcp.stop()


def _call_llm(text: str, prompt_template: str) -> dict:
    """调用 LLM 进行解析"""
    now = datetime.now().strftime("%Y年%m月%d日 %H:%M")
    prompt = prompt_template.format(now=now)

    llm = _get_llm()

    for attempt in range(MAX_RETRIES):
        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            response = llm.invoke([
                SystemMessage(content=prompt),
                HumanMessage(content=text),
            ])
            raw = response.content.strip()
            match = re.search(r"\{[\s\S]*\}", raw)
            if not match:
                raise ValueError(f"AI 未返回 JSON: {raw[:200]}")
            data = json.loads(match.group())
            return _validate(data)
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                prompt = prompt_template.format(now=now) + f"\n\n上次解析错误：{e}，请修正后重新输出 JSON。"
            else:
                return {"error": f"AI 解析失败（已重试{MAX_RETRIES}次）: {e}"}

    return {"error": "未知错误"}


def _extract_keywords(text: str) -> list[str]:
    """简单关键词提取"""
    keywords = ["工作", "个人", "学习", "会议", "健康", "财务",
                "邮件", "报告", "跑步", "阅读", "开会", "提交",
                "提醒", "预约", "整理", "完成", "更新", "讨论",
                "导师", "项目", "文档", "文献"]
    found = [w for w in keywords if w in text]
    return found or ["任务"]


def _extract_time_hint(text: str) -> str | None:
    """提取时间线索"""
    time_words = ["后天", "明天", "今天", "下周", "下个月", "三天后", "下周"]
    for w in time_words:
        if w in text:
            return w
    return None


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
