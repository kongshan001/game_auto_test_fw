# -*- coding: utf-8 -*-
"""
配置文件 - GLM 智能游戏自动化测试

配置优先级: .env 文件 > 系统环境变量 > 默认值
"""

import os
from pathlib import Path

# 加载 .env 文件
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path)
except ImportError:
    pass


def get_env(key: str, default: str = None) -> str:
    return os.environ.get(key, default or "")


def get_env_bool(key: str, default: bool = False) -> bool:
    val = os.environ.get(key, "").lower()
    if val in ("true", "1", "yes", "on"):
        return True
    if val in ("false", "0", "no", "off"):
        return False
    return default


def get_env_int(key: str, default: int = 0) -> int:
    try:
        return int(os.environ.get(key, default))
    except (ValueError, TypeError):
        return default


# ================== GLM API 配置 ==================

GLM_API_KEY = get_env("GLM_API_KEY", "YOUR_API_KEY_HERE")
GLM_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
GLM_MODEL = get_env("GLM_MODEL", "glm-4.6v-flash")
GLM_THINKING = get_env_bool("GLM_THINKING", True)

# ================== 游戏配置 ==================

GAME_NAME = get_env("GAME_NAME", "YourGame")
GAME_EXE_PATH = get_env("GAME_EXE_PATH", r"C:\Games\YourGame\game.exe")

# 进程/窗口识别（用于基于进程截图）
GAME_PROCESS_NAME = get_env("GAME_PROCESS_NAME", "")
GAME_WINDOW_TITLE = get_env("GAME_WINDOW_TITLE", "")

# ================== 测试账号 ==================

TEST_ACCOUNT = get_env("TEST_ACCOUNT", "your_account")
TEST_PASSWORD = get_env("TEST_PASSWORD", "your_password")

# ================== 自动化配置 ==================

BASE_DIR = Path(__file__).parent
SCREENSHOT_DIR = BASE_DIR / "screenshots"
LOG_DIR = BASE_DIR / "logs"
REPORT_DIR = BASE_DIR / "reports"

for d in [SCREENSHOT_DIR, LOG_DIR, REPORT_DIR]:
    d.mkdir(exist_ok=True)

SCREENSHOT_INTERVAL = 0.5
ACTION_DELAY = 1.0
GAME_LOAD_WAIT = 10

MAX_STEPS = get_env_int("MAX_STEPS", 30)
DECISION_TIMEOUT = get_env_int("DECISION_TIMEOUT", 60)
RETRY_TIMES = get_env_int("RETRY_TIMES", 3)

# ================== 测试目标 ==================

TEST_GOALS = {
    "initial": "启动游戏并登录",
    "steps": [
        "等待登录界面出现",
        "输入账号密码",
        "点击登录按钮",
        "选择角色",
        "进入游戏地图",
    ],
    "final": "打开背包界面"
}

# ================== 日志配置 ==================

LOG_LEVEL = get_env("LOG_LEVEL", "INFO")
LOG_FILE = LOG_DIR / "test.log"
