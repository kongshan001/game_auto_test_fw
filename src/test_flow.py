# -*- coding: utf-8 -*-
"""
测试流程编排模块
基于 GLM-4V 的游戏自动化测试流程
"""

import time
from pathlib import Path
from typing import Dict, Any, List

from .glm_vision import GLMVision
from .game_controller import GameController

import sys
sys.path.append(str(Path(__file__).parent.parent))
import config


class TestFlow:
    """测试流程编排"""
    
    def __init__(self):
        self.vision = GLMVision()
        self.controller = GameController()
        self.results = []
        self.screenshot_count = 0
    
    def take_screenshot(self, name: str = None) -> str:
        """截图并返回路径"""
        if name is None:
            self.screenshot_count += 1
            name = f"step_{self.screenshot_count:03d}"
        return self.controller.take_screenshot(name)
    
    def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行单个测试步骤
        
        Args:
            step: 步骤配置
            
        Returns:
            执行结果
        """
        step_name = step.get("step", "未知步骤")
        action = step.get("action")
        
        print(f"\n{'='*50}")
        print(f"📍 执行步骤: {step_name}")
        print(f"{'='*50}")
        
        result = {
            "step": step_name,
            "action": action,
            "success": False,
            "message": ""
        }
        
        try:
            if action == "launch":
                # 启动游戏
                success = self.controller.launch_game()
                result["success"] = success
                result["message"] = "游戏启动成功" if success else "游戏启动失败"
            
            elif action == "click":
                # 点击元素
                target = step.get("target")
                screenshot_path = self.take_screenshot()
                
                # 使用 GLM 找到元素位置
                element = self.vision.find_element(screenshot_path, target)
                
                if element.get("found"):
                    x = element.get("x", 0)
                    y = element.get("y", 0)
                    self.controller.click(x, y)
                    result["success"] = True
                    result["message"] = f"点击 {target} @ ({x}, {y})"
                else:
                    result["message"] = f"未找到元素: {target}"
            
            elif action == "input":
                # 输入文本
                target = step.get("target")
                value = step.get("value", "")
                screenshot_path = self.take_screenshot()
                
                # 找到输入框
                element = self.vision.find_element(screenshot_path, target)
                
                if element.get("found"):
                    x = element.get("x", 0)
                    y = element.get("y", 0)
                    # 先点击输入框
                    self.controller.click(x, y)
                    time.sleep(0.5)
                    # 输入内容
                    self.controller.input_chinese(value)
                    result["success"] = True
                    result["message"] = f"在 {target} 输入: {value}"
                else:
                    result["message"] = f"未找到输入框: {target}"
            
            elif action == "wait_ui":
                # 等待特定 UI 出现
                target = step.get("target")
                max_wait = step.get("max_wait", 30)
                
                start_time = time.time()
                while time.time() - start_time < max_wait:
                    screenshot_path = self.take_screenshot()
                    verify = self.vision.verify_ui_state(screenshot_path, f"显示{target}")
                    
                    if verify.get("matched"):
                        result["success"] = True
                        result["message"] = f"{target} 已出现"
                        break
                    
                    time.sleep(2)
                else:
                    result["message"] = f"等待超时: {target}"
            
            elif action == "wait":
                # 固定等待
                seconds = step.get("seconds", 5)
                self.controller.wait(seconds)
                result["success"] = True
                result["message"] = f"等待 {seconds} 秒"
            
            elif action == "verify":
                # 验证 UI 状态
                target = step.get("target")
                screenshot_path = self.take_screenshot()
                
                verify = self.vision.verify_ui_state(screenshot_path, f"显示{target}")
                result["success"] = verify.get("matched", False)
                result["message"] = verify.get("details", "")
                result["verify_result"] = verify
            
            elif action == "hotkey":
                # 组合键
                keys = step.get("keys", [])
                self.controller.hotkey(*keys)
                result["success"] = True
                result["message"] = f"按下组合键: {'+'.join(keys)}"
            
            else:
                result["message"] = f"未知操作: {action}"
        
        except Exception as e:
            result["message"] = f"执行出错: {str(e)}"
        
        # 记录结果
        self.results.append(result)
        
        # 打印结果
        status = "✅" if result["success"] else "❌"
        print(f"{status} {result['message']}")
        
        return result
    
    def run_test(self, flow: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        运行完整测试流程
        
        Args:
            flow: 测试流程（默认使用 config.TEST_FLOW）
            
        Returns:
            测试报告
        """
        if flow is None:
            flow = config.TEST_FLOW
        
        print("\n" + "="*60)
        print("🎮 GLM 游戏自动化测试开始")
        print("="*60)
        print(f"📋 测试步骤: {len(flow)} 个")
        print(f"🎯 游戏名称: {config.GAME_NAME}")
        print(f"📁 游戏路径: {config.GAME_EXE_PATH}")
        print("="*60 + "\n")
        
        start_time = time.time()
        self.results = []
        self.screenshot_count = 0
        
        for i, step in enumerate(flow, 1):
            print(f"\n[步骤 {i}/{len(flow)}]")
            result = self.execute_step(step)
            
            # 如果关键步骤失败，可以选择继续或中止
            if not result["success"]:
                print(f"⚠️ 步骤失败: {result['message']}")
                # 继续执行下一步
        
        end_time = time.time()
        
        # 生成报告
        report = self.generate_report(start_time, end_time)
        
        return report
    
    def generate_report(self, start_time: float, end_time: float) -> Dict[str, Any]:
        """生成测试报告"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["success"])
        failed = total - passed
        
        report = {
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "pass_rate": f"{passed/total*100:.1f}%" if total > 0 else "0%",
                "duration": f"{end_time - start_time:.1f}s"
            },
            "details": self.results
        }
        
        # 打印报告
        print("\n" + "="*60)
        print("📊 测试报告")
        print("="*60)
        print(f"✅ 通过: {passed}/{total}")
        print(f"❌ 失败: {failed}/{total}")
        print(f"📈 通过率: {report['summary']['pass_rate']}")
        print(f"⏱️ 耗时: {report['summary']['duration']}")
        print("="*60)
        
        # 详细结果
        print("\n详细结果:")
        for i, result in enumerate(self.results, 1):
            status = "✅" if result["success"] else "❌"
            print(f"  {i}. {status} {result['step']}: {result['message']}")
        
        return report


# 测试代码
if __name__ == "__main__":
    flow = TestFlow()
    
    # 简单测试（不启动游戏）
    print("测试 GLM Vision...")
    print(f"API Key 已配置: {'是' if config.GLM_API_KEY != 'YOUR_API_KEY_HERE' else '否'}")
