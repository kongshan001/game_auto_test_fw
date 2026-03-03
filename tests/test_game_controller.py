# -*- coding: utf-8 -*-
"""
游戏控制器模块单元测试
"""

import os
import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import platform

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.game_controller import GameController, WindowInfo, IS_WINDOWS, IS_LINUX


class TestWindowInfo:
    """WindowInfo 类测试"""
    
    def test_window_info_creation(self):
        """测试窗口信息创建"""
        window = WindowInfo(
            handle=12345,
            title="Test Window",
            left=100,
            top=200,
            width=800,
            height=600,
            pid=9999
        )
        
        assert window.handle == 12345
        assert window.title == "Test Window"
        assert window.left == 100
        assert window.top == 200
        assert window.width == 800
        assert window.height == 600
        assert window.pid == 9999
    
    def test_window_rect(self):
        """测试窗口矩形"""
        window = WindowInfo(
            handle=1,
            title="Test",
            left=100,
            top=200,
            width=800,
            height=600
        )
        
        rect = window.rect
        assert rect == (100, 200, 900, 800)
    
    def test_window_center(self):
        """测试窗口中心点"""
        window = WindowInfo(
            handle=1,
            title="Test",
            left=0,
            top=0,
            width=800,
            height=600
        )
        
        center = window.center
        assert center == (400, 300)
    
    def test_window_repr(self):
        """测试窗口字符串表示"""
        window = WindowInfo(
            handle=1,
            title="Test",
            left=0,
            top=0,
            width=100,
            height=100,
            pid=123
        )
        
        repr_str = repr(window)
        assert "Test" in repr_str
        assert "123" in repr_str


class TestGameControllerInit:
    """GameController 初始化测试"""
    
    def test_init_default(self):
        """测试默认初始化"""
        controller = GameController()
        
        assert controller.process_name is None
        assert controller.window_title is None
        assert controller.game_process is None
        assert controller.target_window is None
    
    def test_init_with_params(self):
        """测试带参数初始化"""
        controller = GameController(
            process_name="game.exe",
            window_title="Game Window"
        )
        
        assert controller.process_name == "game.exe"
        assert controller.window_title == "Game Window"
    
    def test_screenshot_dir_created(self):
        """测试截图目录创建"""
        controller = GameController()
        assert controller.screenshot_dir.exists()


class TestFindWindow:
    """窗口查找测试"""
    
    def test_find_window_no_target(self):
        """测试无目标时的窗口查找"""
        controller = GameController()
        result = controller.find_window()
        
        # 没有指定目标时应该返回 None
        assert result is None or isinstance(result, WindowInfo)
    
    @pytest.mark.skipif(not IS_WINDOWS, reason="Windows only")
    def test_list_windows_windows(self):
        """测试 Windows 窗口列表"""
        controller = GameController()
        
        if controller.has_win32:
            windows = controller.list_windows()
            assert isinstance(windows, list)
            # 应该至少有一些窗口
            assert len(windows) >= 0
    
    @pytest.mark.skipif(not IS_LINUX, reason="Linux only")
    def test_list_windows_linux(self):
        """测试 Linux 窗口列表"""
        controller = GameController()
        
        if controller.has_xdotool:
            windows = controller.list_windows()
            assert isinstance(windows, list)


class TestTakeScreenshot:
    """截图测试"""
    
    def test_take_screenshot_creates_file(self, tmp_path):
        """测试截图创建文件"""
        controller = GameController()
        
        # Mock screenshot 返回临时图片
        with patch.object(controller, 'find_window', return_value=None):
            with patch('pyautogui.screenshot') as mock_screenshot:
                from PIL import Image
                test_img = Image.new('RGB', (100, 100), color='red')
                mock_screenshot.return_value = test_img
                
                path = controller.take_screenshot("test_screenshot")
                
                assert os.path.exists(path)
                assert path.endswith(".png")
                
                # 验证图片可打开
                img = Image.open(path)
                assert img.size == (100, 100)
                
                # 清理
                os.remove(path)
    
    def test_take_screenshot_auto_name(self, tmp_path):
        """测试自动命名截图"""
        controller = GameController()
        
        # Mock screenshot
        with patch.object(controller, 'find_window', return_value=None):
            with patch('pyautogui.screenshot') as mock_screenshot:
                from PIL import Image
                test_img = Image.new('RGB', (100, 100), color='blue')
                mock_screenshot.return_value = test_img
                
                path = controller.take_screenshot()
                
                assert os.path.exists(path)
                
                # 验证图片可打开
                img = Image.open(path)
                assert img.size == (100, 100)
                
                # 清理
                os.remove(path)
    
    def test_take_screenshot_returns_valid_image(self):
        """测试截图返回有效图片"""
        from PIL import Image
        
        controller = GameController()
        path = controller.take_screenshot("valid_test")
        
        # 验证可以打开
        img = Image.open(path)
        assert img.size[0] > 0
        assert img.size[1] > 0
        
        # 清理
        os.remove(path)


class TestInputOperations:
    """输入操作测试"""
    
    def test_wait(self):
        """测试等待功能"""
        import time
        
        controller = GameController()
        
        start = time.time()
        controller.wait(0.1)
        elapsed = time.time() - start
        
        assert elapsed >= 0.1
    
    @patch('pyautogui.click')
    def test_click(self, mock_click):
        """测试点击"""
        controller = GameController()
        controller.click(100, 200)
        
        mock_click.assert_called_once()
    
    @patch('pyautogui.press')
    def test_press_key(self, mock_press):
        """测试按键"""
        controller = GameController()
        controller.press_key('enter')
        
        mock_press.assert_called_with('enter')
    
    @patch('pyautogui.hotkey')
    def test_hotkey(self, mock_hotkey):
        """测试组合键"""
        controller = GameController()
        controller.hotkey('ctrl', 'c')
        
        mock_hotkey.assert_called_with('ctrl', 'c')


class TestLaunchGame:
    """游戏启动测试"""
    
    def test_launch_nonexistent_game(self):
        """测试启动不存在的游戏"""
        controller = GameController()
        
        result = controller.launch_game("/nonexistent/game.exe")
        
        assert result == False
    
    def test_launch_game_with_mock(self):
        """测试启动游戏（Mock）"""
        controller = GameController()
        
        with patch('subprocess.Popen') as mock_popen:
            mock_process = Mock()
            mock_process.pid = 12345
            mock_popen.return_value = mock_process
            
            # 创建临时文件模拟游戏
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as f:
                temp_path = f.name
            
            try:
                with patch.dict('config.__dict__', {'GAME_LOAD_WAIT': 0.1}):
                    result = controller.launch_game(temp_path)
                    
                    assert result == True
                    assert controller.game_process == mock_process
            finally:
                os.unlink(temp_path)


class TestSwipe:
    """滑动测试"""
    
    @patch('pyautogui.moveTo')
    @patch('pyautogui.drag')
    def test_swipe_up(self, mock_drag, mock_move):
        """测试向上滑动"""
        controller = GameController()
        controller.swipe("up", distance=100)
        
        mock_move.assert_called_once()
        mock_drag.assert_called_once()
    
    @patch('pyautogui.moveTo')
    @patch('pyautogui.drag')
    def test_swipe_down(self, mock_drag, mock_move):
        """测试向下滑动"""
        controller = GameController()
        controller.swipe("down")
        
        mock_drag.assert_called_once()


class TestGetWindowRect:
    """获取窗口区域测试"""
    
    def test_get_window_rect_no_window(self):
        """测试无窗口时获取区域"""
        controller = GameController()
        
        rect = controller.get_window_rect()
        
        # 无目标窗口时返回 None
        assert rect is None or isinstance(rect, tuple)


# ==================== 集成测试 ====================

class TestIntegration:
    """集成测试"""
    
    def test_full_screenshot_flow(self, tmp_path):
        """测试完整截图流程"""
        controller = GameController()
        
        # Mock screenshot
        with patch.object(controller, 'find_window', return_value=None):
            with patch('pyautogui.screenshot') as mock_screenshot:
                from PIL import Image
                test_img = Image.new('RGB', (800, 600), color='white')
                mock_screenshot.return_value = test_img
                
                # 截图
                path = controller.take_screenshot("integration_test")
                
                # 验证文件存在
                assert os.path.exists(path)
                
                # 验证是有效图片
                img = Image.open(path)
                assert img.format == "PNG"
                
                # 清理
                os.remove(path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
