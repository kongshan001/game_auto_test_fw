# -*- coding: utf-8 -*-
"""
游戏控制器模块
负责游戏启动、截图、鼠标键盘操作

支持基于进程/窗口的截图，而非全屏截图
"""

import os
import sys
import time
import subprocess
import platform
from pathlib import Path
from typing import Optional, Tuple, List
from PIL import Image

sys.path.append(str(Path(__file__).parent.parent))
import config

# 平台检测
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"

# 延迟导入 pyautogui，支持无显示环境
try:
    import pyautogui
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
except Exception:
    # 无显示环境时使用 mock
    from unittest.mock import MagicMock
    pyautogui = MagicMock()
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
    pyautogui.size.return_value = (1920, 1080)
    pyautogui.position.return_value = (960, 540)
    # screenshot 返回一个有效的图片
    from PIL import Image
    pyautogui.screenshot.return_value = Image.new('RGB', (1920, 1080), color='white')


class WindowInfo:
    """窗口信息"""
    def __init__(self, handle: int, title: str, left: int, top: int, width: int, height: int, pid: int = 0):
        self.handle = handle
        self.title = title
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.pid = pid
    
    @property
    def rect(self) -> Tuple[int, int, int, int]:
        """返回 (left, top, right, bottom)"""
        return (self.left, self.top, self.left + self.width, self.top + self.height)
    
    @property
    def center(self) -> Tuple[int, int]:
        """返回窗口中心点"""
        return (self.left + self.width // 2, self.top + self.height // 2)
    
    def __repr__(self):
        return f"WindowInfo(title='{self.title}', rect={self.rect}, pid={self.pid})"


class GameController:
    """
    游戏控制器
    
    支持基于进程/窗口的截图和操作
    """
    
    def __init__(self, process_name: str = None, window_title: str = None):
        """
        初始化控制器
        
        Args:
            process_name: 进程名（如 "game.exe"）
            window_title: 窗口标题（支持部分匹配）
        """
        self.process_name = process_name
        self.window_title = window_title
        self.game_process = None
        self.target_window: Optional[WindowInfo] = None
        
        self.screenshot_dir = Path(config.SCREENSHOT_DIR)
        self.screenshot_dir.mkdir(exist_ok=True)
        
        # 初始化平台相关的窗口管理
        self._init_window_manager()
    
    def _init_window_manager(self):
        """初始化窗口管理器"""
        if IS_WINDOWS:
            self._init_windows()
        elif IS_LINUX:
            self._init_linux()
    
    # ==================== Windows 平台 ====================
    
    def _init_windows(self):
        """初始化 Windows 窗口管理"""
        try:
            import win32gui
            import win32process
            import win32con
            self.win32gui = win32gui
            self.win32process = win32process
            self.win32con = win32con
            self.has_win32 = True
        except ImportError:
            self.has_win32 = False
            print("⚠️ 未安装 pywin32，将使用全屏截图")
            print("   安装: pip install pywin32")
    
    def _find_window_by_pid_windows(self, pid: int) -> Optional[WindowInfo]:
        """通过进程ID查找窗口 (Windows)"""
        if not self.has_win32:
            return None
        
        result = None
        
        def enum_callback(hwnd, _):
            nonlocal result
            _, window_pid = self.win32process.GetWindowThreadProcessId(hwnd)
            if window_pid == pid and self.win32gui.IsWindowVisible(hwnd):
                title = self.win32gui.GetWindowText(hwnd)
                if title:  # 有标题的窗口
                    rect = self.win32gui.GetWindowRect(hwnd)
                    left, top, right, bottom = rect
                    result = WindowInfo(
                        handle=hwnd,
                        title=title,
                        left=left,
                        top=top,
                        width=right - left,
                        height=bottom - top,
                        pid=pid
                    )
                    return False  # 停止枚举
            return True
        
        self.win32gui.EnumWindows(enum_callback, None)
        return result
    
    def _find_window_by_title_windows(self, title_pattern: str) -> Optional[WindowInfo]:
        """通过窗口标题查找窗口 (Windows)"""
        if not self.has_win32:
            return None
        
        result = None
        
        def enum_callback(hwnd, _):
            nonlocal result
            if self.win32gui.IsWindowVisible(hwnd):
                title = self.win32gui.GetWindowText(hwnd)
                if title_pattern.lower() in title.lower():
                    _, pid = self.win32process.GetWindowThreadProcessId(hwnd)
                    rect = self.win32gui.GetWindowRect(hwnd)
                    left, top, right, bottom = rect
                    result = WindowInfo(
                        handle=hwnd,
                        title=title,
                        left=left,
                        top=top,
                        width=right - left,
                        height=bottom - top,
                        pid=pid
                    )
                    return False
            return True
        
        self.win32gui.EnumWindows(enum_callback, None)
        return result
    
    def _get_window_screenshot_windows(self, window: WindowInfo) -> Optional[Image.Image]:
        """截取指定窗口 (Windows)"""
        if not self.has_win32:
            return None
        
        try:
            import win32ui
            import win32con
            
            hwnd = window.handle
            
            # 获取窗口 DC
            hwnd_dc = self.win32gui.GetWindowDC(hwnd)
            mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
            save_dc = mfc_dc.CreateCompatibleDC()
            
            # 创建位图
            save_bitmap = win32ui.CreateBitmap()
            save_bitmap.CreateCompatibleBitmap(mfc_dc, window.width, window.height)
            save_dc.SelectObject(save_bitmap)
            
            # 截图
            result = save_dc.BitBlt((0, 0), (window.width, window.height), mfc_dc, (0, 0), win32con.SRCCOPY)
            
            # 转换为 PIL Image
            bmpinfo = save_bitmap.GetInfo()
            bmpstr = save_bitmap.GetBitmapBits(True)
            img = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1
            )
            
            # 清理
            self.win32gui.DeleteObject(save_bitmap.GetHandle())
            save_dc.DeleteDC()
            mfc_dc.DeleteDC()
            self.win32gui.ReleaseDC(hwnd, hwnd_dc)
            
            return img
            
        except Exception as e:
            print(f"⚠️ 窗口截图失败: {e}")
            return None
    
    # ==================== Linux 平台 ====================
    
    def _init_linux(self):
        """初始化 Linux 窗口管理"""
        try:
            result = subprocess.run(['which', 'xdotool'], capture_output=True)
            self.has_xdotool = result.returncode == 0
            if not self.has_xdotool:
                print("⚠️ 未安装 xdotool，将使用全屏截图")
                print("   安装: sudo apt install xdotool")
        except:
            self.has_xdotool = False
    
    def _find_window_by_pid_linux(self, pid: int) -> Optional[WindowInfo]:
        """通过进程ID查找窗口 (Linux)"""
        if not self.has_xdotool:
            return None
        
        try:
            result = subprocess.run(
                ['xdotool', 'search', '--pid', str(pid)],
                capture_output=True, text=True
            )
            if result.returncode != 0 or not result.stdout.strip():
                return None
            
            window_id = result.stdout.strip().split('\n')[0]
            return self._get_window_info_linux(window_id)
        except:
            return None
    
    def _find_window_by_title_linux(self, title_pattern: str) -> Optional[WindowInfo]:
        """通过窗口标题查找窗口 (Linux)"""
        if not self.has_xdotool:
            return None
        
        try:
            result = subprocess.run(
                ['xdotool', 'search', '--name', title_pattern],
                capture_output=True, text=True
            )
            if result.returncode != 0 or not result.stdout.strip():
                return None
            
            window_id = result.stdout.strip().split('\n')[0]
            return self._get_window_info_linux(window_id)
        except:
            return None
    
    def _get_window_info_linux(self, window_id: str) -> Optional[WindowInfo]:
        """获取窗口信息 (Linux)"""
        try:
            title_result = subprocess.run(
                ['xdotool', 'getwindowname', window_id],
                capture_output=True, text=True
            )
            title = title_result.stdout.strip() if title_result.returncode == 0 else ""
            
            geometry_result = subprocess.run(
                ['xdotool', 'getwindowgeometry', '--shell', window_id],
                capture_output=True, text=True
            )
            
            geometry = {}
            for line in geometry_result.stdout.strip().split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    geometry[key] = int(value)
            
            pid_result = subprocess.run(
                ['xdotool', 'getwindowpid', window_id],
                capture_output=True, text=True
            )
            pid = int(pid_result.stdout.strip()) if pid_result.returncode == 0 else 0
            
            return WindowInfo(
                handle=int(window_id),
                title=title,
                left=geometry.get('X', 0),
                top=geometry.get('Y', 0),
                width=geometry.get('WIDTH', 0),
                height=geometry.get('HEIGHT', 0),
                pid=pid
            )
        except:
            return None
    
    def _get_window_screenshot_linux(self, window: WindowInfo) -> Optional[Image.Image]:
        """截取指定窗口 (Linux)"""
        try:
            result = subprocess.run([
                'import',
                '-window', str(window.handle),
                'png:-'
            ], capture_output=True)
            
            if result.returncode == 0:
                from io import BytesIO
                return Image.open(BytesIO(result.stdout))
        except Exception as e:
            print(f"⚠️ 窗口截图失败: {e}")
        
        return None
    
    # ==================== 通用方法 ====================
    
    def find_window(self) -> Optional[WindowInfo]:
        """查找目标窗口"""
        if self.game_process and self.game_process.pid:
            if IS_WINDOWS:
                window = self._find_window_by_pid_windows(self.game_process.pid)
            else:
                window = self._find_window_by_pid_linux(self.game_process.pid)
            
            if window:
                self.target_window = window
                return window
        
        if self.window_title:
            if IS_WINDOWS:
                window = self._find_window_by_title_windows(self.window_title)
            else:
                window = self._find_window_by_title_linux(self.window_title)
            
            if window:
                self.target_window = window
                return window
        
        if self.process_name:
            pid = self._find_pid_by_name(self.process_name)
            if pid:
                if IS_WINDOWS:
                    window = self._find_window_by_pid_windows(pid)
                else:
                    window = self._find_window_by_pid_linux(pid)
                
                if window:
                    self.target_window = window
                    return window
        
        return None
    
    def _find_pid_by_name(self, process_name: str) -> Optional[int]:
        """通过进程名查找 PID"""
        try:
            if IS_WINDOWS:
                import psutil
                for proc in psutil.process_iter(['pid', 'name']):
                    if proc.info['name'] and proc.info['name'].lower() == process_name.lower():
                        return proc.info['pid']
            else:
                result = subprocess.run(
                    ['pgrep', '-f', process_name],
                    capture_output=True, text=True
                )
                if result.returncode == 0 and result.stdout.strip():
                    return int(result.stdout.strip().split('\n')[0])
        except:
            pass
        return None
    
    def list_windows(self) -> List[WindowInfo]:
        """列出所有可见窗口"""
        windows = []
        
        if IS_WINDOWS and hasattr(self, 'has_win32') and self.has_win32:
            def enum_callback(hwnd, _):
                if self.win32gui.IsWindowVisible(hwnd):
                    title = self.win32gui.GetWindowText(hwnd)
                    if title:
                        _, pid = self.win32process.GetWindowThreadProcessId(hwnd)
                        rect = self.win32gui.GetWindowRect(hwnd)
                        left, top, right, bottom = rect
                        windows.append(WindowInfo(
                            handle=hwnd,
                            title=title,
                            left=left,
                            top=top,
                            width=right - left,
                            height=bottom - top,
                            pid=pid
                        ))
                return True
            
            self.win32gui.EnumWindows(enum_callback, None)
        
        elif IS_LINUX and hasattr(self, 'has_xdotool') and self.has_xdotool:
            result = subprocess.run(
                ['xdotool', 'search', '--onlyvisible', '.'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                for window_id in result.stdout.strip().split('\n'):
                    window = self._get_window_info_linux(window_id)
                    if window and window.title:
                        windows.append(window)
        
        return windows
    
    # ==================== 游戏控制 ====================
    
    def launch_game(self, exe_path: str = None) -> bool:
        """启动游戏"""
        exe_path = exe_path or config.GAME_EXE_PATH
        
        if not os.path.exists(exe_path):
            print(f"❌ 游戏路径不存在: {exe_path}")
            return False
        
        print(f"🎮 启动游戏: {exe_path}")
        
        try:
            self.game_process = subprocess.Popen(exe_path)
            print(f"✅ 游戏已启动，PID: {self.game_process.pid}")
            
            print(f"⏳ 等待游戏加载 {config.GAME_LOAD_WAIT} 秒...")
            time.sleep(config.GAME_LOAD_WAIT)
            
            window = self.find_window()
            if window:
                print(f"✅ 找到窗口: {window.title}")
            else:
                print("⚠️ 未找到游戏窗口，将使用全屏模式")
            
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
        """截取目标窗口（或全屏）"""
        if save_name is None:
            save_name = f"screenshot_{int(time.time())}"
        
        save_path = self.screenshot_dir / f"{save_name}.png"
        
        window = self.find_window()
        img = None
        
        if window:
            if IS_WINDOWS:
                img = self._get_window_screenshot_windows(window)
            elif IS_LINUX:
                img = self._get_window_screenshot_linux(window)
            
            if img:
                print(f"📸 窗口截图: {window.title} ({window.width}x{window.height})")
        
        if img is None:
            print("📸 使用全屏截图")
            img = pyautogui.screenshot()
        
        img.save(save_path)
        return str(save_path)
    
    def activate_window(self) -> bool:
        """激活目标窗口（置顶）"""
        window = self.find_window()
        if not window:
            return False
        
        try:
            if IS_WINDOWS and hasattr(self, 'has_win32') and self.has_win32:
                self.win32gui.SetForegroundWindow(window.handle)
            elif IS_LINUX and hasattr(self, 'has_xdotool') and self.has_xdotool:
                subprocess.run(['xdotool', 'windowactivate', str(window.handle)])
            return True
        except:
            return False
    
    # ==================== 输入操作 ====================
    
    def click(self, x: int, y: int, clicks: int = 1, button: str = 'left', relative: bool = True):
        """点击"""
        if relative and self.target_window:
            x = self.target_window.left + x
            y = self.target_window.top + y
        
        print(f"👆 点击: ({x}, {y})")
        pyautogui.click(x, y, clicks=clicks, button=button)
        time.sleep(config.ACTION_DELAY)
    
    def input_text(self, text: str, interval: float = 0.05):
        """输入文本"""
        print(f"⌨️ 输入: {text}")
        pyautogui.write(text, interval=interval)
        time.sleep(config.ACTION_DELAY)
    
    def input_chinese(self, text: str):
        """输入中文（通过剪贴板）"""
        print(f"⌨️ 输入中文: {text}")
        try:
            import pyperclip
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(config.ACTION_DELAY)
        except ImportError:
            print("⚠️ 需要安装 pyperclip: pip install pyperclip")
    
    def press_key(self, key: str):
        """按下按键"""
        print(f"🔑 按键: {key}")
        pyautogui.press(key)
        time.sleep(config.ACTION_DELAY)
    
    def hotkey(self, *keys):
        """组合键"""
        print(f"🔑 组合键: {'+'.join(keys)}")
        pyautogui.hotkey(*keys)
        time.sleep(config.ACTION_DELAY)
    
    def swipe(self, direction: str = "up", distance: int = 200):
        """滑动"""
        window = self.target_window
        if window:
            cx, cy = window.center
        else:
            cx, cy = pyautogui.size()
            cx, cy = cx // 2, cy // 2
        
        dx, dy = {
            "up": (0, -distance),
            "down": (0, distance),
            "left": (-distance, 0),
            "right": (distance, 0)
        }.get(direction, (0, 0))
        
        print(f"👆 滑动: {direction}")
        pyautogui.moveTo(cx, cy)
        pyautogui.drag(dx, dy, duration=0.5)
        time.sleep(config.ACTION_DELAY)
    
    def wait(self, seconds: float):
        """等待"""
        print(f"⏳ 等待 {seconds} 秒")
        time.sleep(seconds)
    
    def get_window_rect(self) -> Optional[Tuple[int, int, int, int]]:
        """获取目标窗口区域"""
        window = self.find_window()
        if window:
            return window.rect
        return None


if __name__ == "__main__":
    print("🎮 游戏控制器测试")
    print(f"平台: {platform.system()}")
    
    controller = GameController()
    
    print("\n📋 当前窗口列表:")
    windows = controller.list_windows()
    for i, w in enumerate(windows[:10]):
        print(f"  [{i}] {w.title[:40]:<40} PID:{w.pid}")
    
    print("\n📸 测试截图:")
    path = controller.take_screenshot("test")
    print(f"   保存到: {path}")
