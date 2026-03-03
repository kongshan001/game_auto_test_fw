# -*- coding: utf-8 -*-
"""
自动测试器模块单元测试
"""

import os
import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.auto_tester import AutoGameTester


class TestAutoGameTesterInit:
    """AutoGameTester 初始化测试"""
    
    def test_init_default(self):
        """测试默认初始化"""
        with patch('src.auto_tester.GLMVision') as mock_vision, \
             patch('src.auto_tester.GameController') as mock_controller:
            tester = AutoGameTester()
            
            assert tester.step_count == 0
            assert tester.history == []
    
    def test_init_with_params(self):
        """测试带参数初始化"""
        with patch('src.auto_tester.GLMVision') as mock_vision, \
             patch('src.auto_tester.GameController') as mock_controller:
            tester = AutoGameTester(
                api_key="test_key",
                model="test_model",
                thinking=False
            )
            
            assert tester.thinking == False


class TestBuildContext:
    """上下文构建测试"""
    
    def test_build_context_empty(self):
        """测试空历史上下文"""
        with patch('src.auto_tester.GLMVision'), \
             patch('src.auto_tester.GameController'):
            tester = AutoGameTester()
            
            context = tester._build_context()
            
            assert context is None
    
    def test_build_context_with_history(self):
        """测试有历史记录的上下文"""
        with patch('src.auto_tester.GLMVision'), \
             patch('src.auto_tester.GameController'):
            tester = AutoGameTester()
            
            # 添加模拟历史
            tester.history = [
                {"step": 1, "decision": {"action": "click"}},
                {"step": 2, "decision": {"action": "wait"}},
                {"step": 3, "decision": {"action": "input"}}
            ]
            
            context = tester._build_context()
            
            assert context is not None
            assert "click" in context
            assert "wait" in context
            assert "input" in context
    
    def test_build_context_limits_to_recent(self):
        """测试上下文限制为最近记录"""
        with patch('src.auto_tester.GLMVision'), \
             patch('src.auto_tester.GameController'):
            tester = AutoGameTester()
            
            # 添加超过 3 条历史
            tester.history = [
                {"step": i, "decision": {"action": f"action_{i}"}}
                for i in range(1, 6)
            ]
            
            context = tester._build_context()
            
            # 应该只包含最近 3 条
            assert "action_5" in context
            assert "action_4" in context
            assert "action_3" in context
            assert "action_2" not in context  # 太旧了


class TestExecuteAction:
    """动作执行测试"""
    
    def test_execute_click_action(self):
        """测试执行点击动作"""
        with patch('src.auto_tester.GLMVision') as mock_vision_cls, \
             patch('src.auto_tester.GameController') as mock_controller_cls:
            
            mock_controller = Mock()
            mock_controller_cls.return_value = mock_controller
            mock_vision_cls.return_value = Mock()
            
            tester = AutoGameTester()
            
            decision = {
                "action": "click",
                "x": 100,
                "y": 200,
                "target": "button"
            }
            
            result = tester._execute_action(decision, "screenshot.png")
            
            mock_controller.click.assert_called_once()
            assert result["success"] == True
    
    def test_execute_click_find_element(self):
        """测试点击时查找元素"""
        with patch('src.auto_tester.GLMVision') as mock_vision_cls, \
             patch('src.auto_tester.GameController') as mock_controller_cls:
            
            mock_controller = Mock()
            mock_controller_cls.return_value = mock_controller
            
            mock_vision = Mock()
            mock_vision.find_element.return_value = {"found": True, "x": 150, "y": 250}
            mock_vision_cls.return_value = mock_vision
            
            tester = AutoGameTester()
            
            decision = {
                "action": "click",
                "target": "button"
                # 没有 x, y
            }
            
            result = tester._execute_action(decision, "screenshot.png")
            
            mock_vision.find_element.assert_called_once()
            mock_controller.click.assert_called()
    
    def test_execute_wait_action(self):
        """测试执行等待动作"""
        with patch('src.auto_tester.GLMVision') as mock_vision_cls, \
             patch('src.auto_tester.GameController') as mock_controller_cls:
            
            mock_controller = Mock()
            mock_controller_cls.return_value = mock_controller
            mock_vision_cls.return_value = Mock()
            
            tester = AutoGameTester()
            
            decision = {"action": "wait", "seconds": 2}
            
            result = tester._execute_action(decision, "screenshot.png")
            
            mock_controller.wait.assert_called_with(2)
            assert result["success"] == True
    
    def test_execute_input_action(self):
        """测试执行输入动作"""
        with patch('src.auto_tester.GLMVision') as mock_vision_cls, \
             patch('src.auto_tester.GameController') as mock_controller_cls:
            
            mock_controller = Mock()
            mock_controller_cls.return_value = mock_controller
            
            mock_vision = Mock()
            mock_vision.find_element.return_value = {"found": True, "x": 100, "y": 100}
            mock_vision_cls.return_value = mock_vision
            
            tester = AutoGameTester()
            
            decision = {
                "action": "input",
                "target": "input field",
                "text": "hello"
            }
            
            result = tester._execute_action(decision, "screenshot.png")
            
            mock_controller.input_chinese.assert_called_with("hello")
    
    def test_execute_swipe_action(self):
        """测试执行滑动动作"""
        with patch('src.auto_tester.GLMVision') as mock_vision_cls, \
             patch('src.auto_tester.GameController') as mock_controller_cls:
            
            mock_controller = Mock()
            mock_controller_cls.return_value = mock_controller
            mock_vision_cls.return_value = Mock()
            
            tester = AutoGameTester()
            
            decision = {"action": "swipe", "direction": "up"}
            
            result = tester._execute_action(decision, "screenshot.png")
            
            mock_controller.swipe.assert_called_with("up")
            assert result["success"] == True
    
    def test_execute_done_action(self):
        """测试完成动作"""
        with patch('src.auto_tester.GLMVision'), \
             patch('src.auto_tester.GameController'):
            
            tester = AutoGameTester()
            
            decision = {"action": "done"}
            
            result = tester._execute_action(decision, "screenshot.png")
            
            # done 不需要执行任何操作
            assert result["action"] == "done"


class TestCheckFinalGoal:
    """最终目标检查测试"""
    
    def test_check_final_goal_achieved(self):
        """测试目标达成"""
        with patch('src.auto_tester.GLMVision') as mock_vision_cls, \
             patch('src.auto_tester.GameController'):
            
            mock_vision = Mock()
            mock_vision.verify_state.return_value = {"matched": True, "confidence": 0.95}
            mock_vision_cls.return_value = mock_vision
            
            tester = AutoGameTester()
            
            result = tester._check_final_goal("screen.png", "login page")
            
            assert result == True
    
    def test_check_final_goal_not_achieved(self):
        """测试目标未达成"""
        with patch('src.auto_tester.GLMVision') as mock_vision_cls, \
             patch('src.auto_tester.GameController'):
            
            mock_vision = Mock()
            mock_vision.verify_state.return_value = {"matched": False, "confidence": 0.3}
            mock_vision_cls.return_value = mock_vision
            
            tester = AutoGameTester()
            
            result = tester._check_final_goal("screen.png", "login page")
            
            assert result == False
    
    def test_check_final_goal_low_confidence(self):
        """测试低置信度"""
        with patch('src.auto_tester.GLMVision') as mock_vision_cls, \
             patch('src.auto_tester.GameController'):
            
            mock_vision = Mock()
            mock_vision.verify_state.return_value = {"matched": True, "confidence": 0.5}
            mock_vision_cls.return_value = mock_vision
            
            tester = AutoGameTester()
            
            result = tester._check_final_goal("screen.png", "login page")
            
            # 置信度 < 0.8 不算达成
            assert result == False


class TestRun:
    """运行测试"""
    
    @patch('src.auto_tester.GLMVision')
    @patch('src.auto_tester.GameController')
    def test_run_max_steps_reached(self, mock_controller_cls, mock_vision_cls):
        """测试达到最大步数"""
        mock_controller = Mock()
        mock_controller.take_screenshot.return_value = "screen.png"
        mock_controller_cls.return_value = mock_controller
        
        mock_vision = Mock()
        mock_vision.decide_action.return_value = {"action": "wait", "seconds": 0.1}
        mock_vision_cls.return_value = mock_vision
        
        tester = AutoGameTester()
        
        with patch.dict('config.__dict__', {'MAX_STEPS': 2, 'ACTION_DELAY': 0}):
                report = tester.run(
                    initial_goal="test",
                    final_goal="done",
                    max_steps=2
                )
        
        assert report["steps"] == 2
        assert report["success"] == False  # 未完成
    
    @patch('src.auto_tester.GLMVision')
    @patch('src.auto_tester.GameController')
    def test_run_goal_achieved(self, mock_controller_cls, mock_vision_cls):
        """测试目标达成"""
        mock_controller = Mock()
        mock_controller.take_screenshot.return_value = "screen.png"
        mock_controller_cls.return_value = mock_controller
        
        mock_vision = Mock()
        mock_vision.decide_action.return_value = {"action": "done"}
        mock_vision_cls.return_value = mock_vision
        
        tester = AutoGameTester()
        
        with patch.dict('config.ACTION_DELAY', 0):
            report = tester.run(
                initial_goal="test",
                final_goal="done",
                max_steps=10
            )
        
        assert report["success"] == True
    
    @patch('src.auto_tester.GLMVision')
    @patch('src.auto_tester.GameController')
    def test_run_records_history(self, mock_controller_cls, mock_vision_cls):
        """测试记录历史"""
        mock_controller = Mock()
        mock_controller.take_screenshot.return_value = "screen.png"
        mock_controller_cls.return_value = mock_controller
        
        mock_vision = Mock()
        mock_vision.decide_action.return_value = {"action": "done"}
        mock_vision_cls.return_value = mock_vision
        
        tester = AutoGameTester()
        
        with patch.dict('config.ACTION_DELAY', 0):
            tester.run(initial_goal="test", final_goal="done", max_steps=5)
        
        assert len(tester.history) >= 1
        assert "step" in tester.history[0]
        assert "decision" in tester.history[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
