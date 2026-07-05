"""PyWebView 启动入口"""
import argparse
import sys
import os
import threading
import webview
from http.server import HTTPServer, SimpleHTTPRequestHandler

# 确保 backend 包可被导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.database import init_db, seed_reset
from backend.api.handlers import (
    api_get_tasks,
    api_add_task,
    api_update_task,
    api_delete_task,
    api_toggle_task,
    api_register,
    api_login,
    api_get_current_user,
    api_logout,
    api_get_guest_task_count,
    api_bind_guest_tasks,
    api_unbind_user_tasks,
)


class ApiBridge:
    """暴露给前端的 API 对象"""
    api_get_tasks = staticmethod(api_get_tasks)
    api_add_task = staticmethod(api_add_task)
    api_update_task = staticmethod(api_update_task)
    api_delete_task = staticmethod(api_delete_task)
    api_toggle_task = staticmethod(api_toggle_task)
    api_register = staticmethod(api_register)
    api_login = staticmethod(api_login)
    api_get_current_user = staticmethod(api_get_current_user)
    api_logout = staticmethod(api_logout)
    api_get_guest_task_count = staticmethod(api_get_guest_task_count)
    api_bind_guest_tasks = staticmethod(api_bind_guest_tasks)
    api_unbind_user_tasks = staticmethod(api_unbind_user_tasks)


class QuietHandler(SimpleHTTPRequestHandler):
    """静默 HTTP 处理器，不打印请求日志"""
    def log_message(self, format, *args):
        pass


def _start_http_server(dist_dir, port):
    """在独立线程中启动 HTTP 服务器 serve dist 目录"""
    os.chdir(dist_dir)
    server = HTTPServer(("127.0.0.1", port), QuietHandler)
    server.serve_forever()


def _find_free_port():
    """找一个空闲端口"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", action="store_true", help="清空 tasks 并重新注入种子数据")
    args = parser.parse_args()

    init_db()

    if args.seed:
        count = seed_reset()
        print(f"种子数据已重新注入，共 {count} 条")

    bridge = ApiBridge()

    # Vite 构建产物路径
    dist_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
    index_path = os.path.join(dist_dir, "index.html")

    if os.path.exists(index_path):
        port = _find_free_port()
        threading.Thread(target=_start_http_server, args=(dist_dir, port), daemon=True).start()
        url = f"http://127.0.0.1:{port}"
        print(f"Serving dist on {url}")
    else:
        print("未找到 dist 构建产物，请先执行 npm run build")
        url = "http://localhost:5173"

    window = webview.create_window(
        "TodoMaster",
        url=url,
        js_api=bridge,
        width=1200,
        height=800,
        min_size=(800, 600),
    )
    webview.start()


if __name__ == "__main__":
    main()
