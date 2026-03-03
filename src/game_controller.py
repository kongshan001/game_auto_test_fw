# -*- coding: utf-8 -*-
"""
游戏控制器模块
负责游戏启动、截图、鼠标键盘操作
"""

import os
import time
import subprocess
from pathlib import Path
from typing import Optional, Tuple

import pyautogui
from PIL import Image
import mss

import sys
sys.path.append(str(Path(__file__).parent.parent))
import config

# 安全设置：防止失控
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5


class GameController:
    """游戏控制器"""
    
    def __init__(self):
        self.screenshot_dir = Path(config.SCREENSHOT_DIR)
        self.screenshot_dir.mkdir(exist_ok=True)
        self.game_process = None
        self.sct = mss.mss()
    
    def launch_game(self) -> bool:
        """
        启动游戏
        
        Returns:
            是否启动成功
        """
        exe_path = config.GAME_EXE_PATH
        
        if not os.path.exists(exe_path):
            print(f"❌ 游戏路径不存在: {exe_path}")
            return False
        
        print(f"🎮 启动游戏: {exe_path}")
        
        try:
            self.game_process = subprocess.Popen(exe_path)
            print(f"✅ 游戏已启动，PID: {self.game_process.pid}")
            
            # 等待游戏加载
            wait_time = config.GAME_LOAD_WAIT
            print(f"⏳ 等待游戏加载 {wait_time} 秒...")
            time.sleep(wait_time)
            
            return True
        except Exception as e:
            print(f"❌ 启动失败: {e}")
            return False
    
    def close_game(self):
        """关闭游戏"""
        if self.game_process:
            self.game_process.terminate()
            print("🎮 游戏已关闭")
    
    def take_screenshot(self, save_name: str = None) -> str:
        """
        截取屏幕
        
        Args:
            save_name: 保存文件名（不含扩展名）
            
        Returns:
            截图文件路径
        """
        if save_name is None:
            save_name = f"screenshot_{int(time.time())}"
        
        save_path = self.screenshot_dir / f"{save_name}.png"
        
        # 使用 mss 截图（更快）
        screenshot = self.sct.monitors[1]  # 主显示器
        img = self.sct.grab(screenshot)
        
        # 保存
        from PIL import Image
        pil_img = Image.frombytes('RGB', img.size, img.bgra, 'raw', 'BGRX')
        pil_img.save(save_path)
        
        print(f"📸 截图已保存: {save_path}")
        return str(save_path)
    
    def click(self, x: int, y: int, clicks: int = 1, button: str = 'left'):
        """
        点击指定位置
        
        Args:
            x: X 坐标
            y: Y 坐标
            clicks: 点击次数
            button: 鼠标按钮 ('left', 'right', 'middle')
        """
        print(f"👆 点击: ({x}, {y})")
        pyautogui.click(x, y, clicks=clicks, button=button)
        time.sleep(config.ACTION_DELAY)
    
    def double_click(self, x: int, y: int):
        """双击"""
        self.click(x, y, clicks=2)
    
    def right_click(self, x: int, y: int):
        """右键点击"""
        self.click(x, y, button='right')
    
    def input_text(self, text: str, interval: float = 0.05):
        """
        输入文本
        
        Args:
            text: 要输入的文本
            interval: 字符间隔
        """
        print(f"⌨️ 输入: {text}")
        pyautogui.write(text, interval=interval)
        time.sleep(config.ACTION_DELAY)
    
    def input_chinese(self, text: str):
        """
        输入中文（使用剪贴板）
        
        Args:
            text: 中文文本
        """
        print(f"⌨️ 输入中文: {text}")
        # 使用 pyperclip 复制粘贴
        try:
            import pyperclip
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(config.ACTION_DELAY)
        except ImportError:
            print("⚠️ 需要安装 pyperclip: pip install pyperclip")
    
    def press_key(self, key: str):
        """
        按下按键
        
        Args:
            key: 按键名称（如 'enter', 'esc', 'space'）
        """
        print(f"🔑 按键: {key}")
        pyautogui.press(key)
        time.sleep(config.ACTION_DELAY)
    
    def hotkey(self, *keys):
        """
        组合键
        
        Args:
            keys: 按键组合（如 'ctrl', 'c'）
        """
        print(f"🔑 组合键: {'+'.join(keys)}")
        pyautogui.hotkey(*keys)
        time.sleep(config.ACTION_DELAY)
    
    def scroll(self, clicks: int, x: int = None, y: int = None):
        """
        滚动鼠标滚轮
        
        Args:
            clicks: 滚动次数（正数向上，负数向下）
            x: X 坐标（可选）
            y: Y 坐标（可选）
        """
        print(f"🖱️ 滚动: {clicks}")
        pyautogui.scroll(clicks, x, y)
        time.sleep(config.ACTION_DELAY)
    
    def move_to(self, x: int, y: int, duration: float = 0.5):
        """
        移动鼠标到指定位置
        
        Args:
            x: X 坐标
            y: Y 坐标
            duration: 移动时间
        """
        print(f"🖱️ 移动: ({x}, {y})")
        pyautogui.moveTo(x, y, duration=duration)
    
    def drag_to(self, x: int, y: int, duration: float = 0.5):
        """
        拖拽到指定位置
        
        Args:
            x: 目标 X 坐标
            y: 目标 Y 坐标
            duration: 拖拽时间
        """
        print(f"🖱️ 拖拽: ({x}, {y})")
        pyautogui.dragTo(x, y, duration=duration)
        time.sleep(config.ACTION_DELAY)
    
    def wait(self, seconds: float):
        """
        等待
        
        Args:
            seconds: 等待秒数
        """
        print(f"⏳ 等待 {seconds} 秒")
        time.sleep(seconds)
    
    def get_screen_size(self) -> Tuple[int, int]:
        """获取屏幕尺寸"""
        return pyautogui.size()
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """获取鼠标当前位置"""
        return pyautogui.position()


# 测试代码
if __name__ == "__main__":
    controller = GameController()
    
    print("🎮 游戏控制器测试")
    print(f"屏幕尺寸: {controller.get_screen_size()}")
    print(f"鼠标位置: {controller.get_mouse_position()}")
    
    # 测试截图
    screenshot_path = controller.take_screenshot("test")
    print(f"截图保存: {screenshot_path}")
