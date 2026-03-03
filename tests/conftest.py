# -*- coding: utf-8 -*-
"""
pytest 配置文件 - Mock pyautogui 以支持无显示环境测试
"""

import sys
from unittest.mock import MagicMock

# 创建 pyautogui mock
pyautogui_mock = MagicMock()

# 设置一些基本属性
pyautogui_mock.FAILSAFE = True
pyautogui_mock.PAUSE = 0.1
pyautogui_mock.size.return_value = (1920, 1080)
pyautogui_mock.position.return_value = (960, 540)

# 在导入 src 模块之前 mock pyautogui
sys.modules['pyautogui'] = pyautogui_mock
sys.modules['mouseinfo'] = MagicMock()
sys.modules['pyperclip'] = MagicMock()

# 添加项目路径
import pytest
from pathlib import Path

@pytest.fixture
def mock_pyautogui():
    """返回 pyautogui mock"""
    return pyautogui_mock
