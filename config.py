# -*- coding: utf-8 -*-
"""
配置文件 - GLM 智能游戏自动化测试

参考文档: https://docs.bigmodel.cn/cn/guide/models/vlm/glm-4.6v
"""

import os
from pathlib import Path

# ================== GLM API 配置 ==================

GLM_API_KEY = os.environ.get("GLM_API_KEY", "YOUR_API_KEY_HERE")
GLM_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

# GLM-4.6V 系列模型选择
# glm-4.6v: 旗舰版 (106B)，最强视觉理解
# glm-4.6v-flashx: 轻量高速版 (9B)，速度优先
# glm-4.6v-flash: 完全免费版，适合测试
GLM_MODEL = os.environ.get("GLM_MODEL", "glm-4.6v-flash")

# 是否开启深度思考模式
# 开启后模型会进行更深入的分析，但响应时间稍长
GLM_THINKING = os.environ.get("GLM_THINKING", "true").lower() == "true"

# ================== 游戏配置 ==================

GAME_NAME = os.environ.get("GAME_NAME", "YourGame")
GAME_EXE_PATH = os.environ.get("GAME_EXE_PATH", r"C:\Games\YourGame\game.exe")

# ================== 测试账号 ==================

TEST_ACCOUNT = os.environ.get("TEST_ACCOUNT", "your_account")
TEST_PASSWORD = os.environ.get("TEST_PASSWORD", "your_password")

# ================== 自动化配置 ==================

# 截图
SCREENSHOT_DIR = Path("./screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)
SCREENSHOT_INTERVAL = 0.5  # 截图间隔（秒）

# 操作延迟
ACTION_DELAY = 1.0  # 操作后等待时间
GAME_LOAD_WAIT = 10  # 游戏启动等待时间

# 智能决策
MAX_STEPS = 30  # 单次测试最大步数
DECISION_TIMEOUT = 60  # 单次决策超时（秒）
RETRY_TIMES = 3  # 失败重试次数

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

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOG_DIR = Path("./logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "test.log"

# ================== 报告配置 ==================

REPORT_DIR = Path("./reports")
REPORT_DIR.mkdir(exist_ok=True)
