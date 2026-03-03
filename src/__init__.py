# -*- coding: utf-8 -*-
"""
GLM 游戏自动化测试模块
"""

# 延迟导入，避免在无显示环境下导入失败

def __getattr__(name):
    if name == 'GLMVision':
        from .glm_vision import GLMVision
        return GLMVision
    elif name == 'GameController':
        from .game_controller import GameController
        return GameController
    elif name == 'AutoGameTester':
        from .auto_tester import AutoGameTester
        return AutoGameTester
    elif name == 'run_test':
        from .auto_tester import run_test
        return run_test
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ['GLMVision', 'GameController', 'AutoGameTester', 'run_test']
