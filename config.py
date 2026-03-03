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
    # 优先加载项目目录下的 .env
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv 未安装时使用系统环境变量


def get_env(key: str, default: str = None) -> str:
    """获取环境变量"""
    return os.environ.get(key, default or "")


def get_env_bool(key: str, default: bool = False) -> bool:
    """获取布尔型环境变量"""
    val = os.environ.get(key, "").lower()
    if val in ("true", "1", "yes", "on"):
        return True
    if val in ("false", "0", "no", "off"):
        return False
    return default


def get_env_int(key: str, default: int = 0) -> int:
    """获取整型环境变量"""
    try:
        return int(os.environ.get(key, default))
    except (ValueError, TypeError):
        return default


# ================== GLM API 配置 ==================

GLM_API_KEY = get_env("GLM_API_KEY", "YOUR_API_KEY_HERE")
GLM_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

# GLM-4.6V 系列模型
GLM_MODEL = get_env("GLM_MODEL", "glm-4.6v-flash")

# 深度思考模式
GLM_THINKING = get_env_bool("GLM_THINKING", True)

# ================== 游戏配置 ==================

GAME_NAME = get_env("GAME_NAME", "YourGame")
GAME_EXE_PATH = get_env("GAME_EXE_PATH", r"C:\Games\YourGame\game.exe")

# ================== 测试账号 ==================

TEST_ACCOUNT = get_env("TEST_ACCOUNT", "your_account")
TEST_PASSWORD = get_env("TEST_PASSWORD", "your_password")

# ================== 自动化配置 ==================

# 目录
BASE_DIR = Path(__file__).parent
SCREENSHOT_DIR = BASE_DIR / "screenshots"
LOG_DIR = BASE_DIR / "logs"
REPORT_DIR = BASE_DIR / "reports"

# 确保目录存在
for d in [SCREENSHOT_DIR, LOG_DIR, REPORT_DIR]:
    d.mkdir(exist_ok=True)

# 时间配置
SCREENSHOT_INTERVAL = 0.5
ACTION_DELAY = 1.0
GAME_LOAD_WAIT = 10

# 智能决策
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
