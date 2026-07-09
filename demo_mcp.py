"""MCP Sequential Thinking 展示/测试脚本

用法：
    python demo_mcp.py                           # 使用示例输入
    python demo_mcp.py "明天下午开会讨论项目"       # 自定义输入
    python demo_mcp.py --quick                    # 仅快速模式（不用 MCP）
"""
import sys
import os
import io
import time

# Windows 终端 GBK 编码兼容
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DEEPSEEK_API_KEY", open(".env").read().split("DEEPSEEK_API_KEY=")[1].split("\n")[0].strip() if os.path.exists(".env") else "")

from backend.services.ai_service import parse, parse_with_thinking


def demo_quick(text: str) -> dict:
    """快速模式——直接 LLM 解析"""
    print("\n" + "=" * 60)
    print("  模式: 快速解析 (直接 LLM)")
    print("=" * 60)
    t0 = time.time()
    result = parse(text)
    elapsed = time.time() - t0
    print(f"  耗时: {elapsed:.1f}s")
    print(f"  结果: {_format_result(result)}")
    return result


def demo_mcp(text: str) -> dict:
    """MCP 推理模式——5 阶段 Sequential Thinking"""
    print("\n" + "=" * 60)
    print("  模式: MCP Sequential Thinking (5 阶段推理)")
    print("  流程: Problem Definition → Research → Analysis → Synthesis → Conclusion")
    print("=" * 60)

    print(f"\n  输入: {text}")
    print(f"  当前时间: {_now()}")

    t0 = time.time()
    result = parse_with_thinking(text)
    elapsed = time.time() - t0

    print(f"\n  耗时: {elapsed:.1f}s")
    actual_mode = result.get('mode', '直接解析')
    print(f"  模式: {actual_mode}")
    print(f"  结果: {_format_result(result)}")

    # 说明 MCP 端日志
    import glob
    log_dir = os.path.expanduser("~/.mcp_sequential_thinking")
    if os.path.exists(log_dir):
        latest = sorted(glob.glob(f"{log_dir}/*.jsonl"), key=os.path.getmtime)
        if latest:
            with open(latest[-1], encoding="utf-8") as f:
                lines = f.readlines()
            print(f"\n  推理日志: {len(lines)} 条记录, 文件: {latest[-1]}")
    return result


def demo_both(text: str):
    """对比演示——快速 vs MCP"""
    print("\n" + "╔" + "═" * 58 + "╗")
    print(f"║  输入: {text}" + " " * (56 - len(text) - len("输入: ")) + "║")
    print("╚" + "═" * 58 + "╝")

    demo_quick(text)
    demo_mcp(text)

    print("\n" + "=" * 60)
    print("  结论: MCP 推理模式将解析过程结构化，每步可追踪、可审计。")
    print("  MCP 不可用时自动降级为快速模式，系统不受影响。")
    print("=" * 60)


# ── 辅助函数 ──

def _now():
    from datetime import datetime
    return datetime.now().strftime("%Y年%m月%d日 %H:%M")

def _format_result(r: dict) -> str:
    if r.get("error"):
        return f"X {r['error']}"
    return f"title={r.get('title')}, priority={r.get('priority')}, due={r.get('due_date','')[:16]}, tags={r.get('tags')}"


# ── 入口 ──

if __name__ == "__main__":
    if "--quick" in sys.argv:
        args = [a for a in sys.argv[1:] if a != "--quick"]
        text = args[0] if args else "后天下午3点提醒我给导师发邮件，顺便查一下最新文献"
        demo_quick(text)
    else:
        args = [a for a in sys.argv[1:] if not a.startswith("--")]
        text = args[0] if args else "后天下午3点提醒我给导师发邮件，顺便查一下最新文献"
        demo_both(text)
