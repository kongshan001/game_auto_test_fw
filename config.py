# -*- coding: utf-8 -*-
"""
配置文件 - GLM 智能游戏自动化测试
"""

# ================== GLM API 配置 ==================
# 从环境变量或直接填写
import os

GLM_API_KEY = os.environ.get("GLM_API_KEY", "YOUR_API_KEY_HERE")
GLM_API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

# 多模态模型选择
# glm-4v-flash: 免费额度，速度快
# glm-4v: 更强大，收费
GLM_MODEL = "glm-4v-flash"

# ================== 游戏配置 ==================
GAME_NAME = "YourGame"
GAME_EXE_PATH = r"C:\Games\YourGame\game.exe"

# ================== 测试账号 ==================
TEST_ACCOUNT = "your_account"
TEST_PASSWORD = "your_password"

# ================== 自动化配置 ==================
# 截图
SCREENSHOT_DIR = "./screenshots"
SCREENSHOT_INTERVAL = 0.5

# 操作延迟
ACTION_DELAY = 1.0
GAME_LOAD_WAIT = 10

# 智能决策
MAX_STEPS = 30          # 最大步数
DECISION_TIMEOUT = 30   # 决策超时（秒）
RETRY_TIMES = 3         # 失败重试次数

# ================== 测试目标 ==================
# 自动化测试的目标描述
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
LOG_LEVEL = "INFO"
LOG_FILE = "./logs/test.log"
