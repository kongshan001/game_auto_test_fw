# -*- coding: utf-8 -*-
"""
智能游戏自动化测试器 - 完全无人值守
"""

import time
import json
from pathlib import Path

from .glm_vision import GLMVision
from .game_controller import GameController

import sys
sys.path.append(str(Path(__file__).parent.parent))
import config


class AutoGameTester:
    """智能游戏自动化测试器"""
    
    def __init__(self):
        self.vision = GLMVision()
        self.controller = GameController()
        self.step_count = 0
    
    def run(self, initial_goal: str = None, final_goal: str = None, max_steps: int = 30) -> dict:
        """
        运行自动化测试
        
        Args:
            initial_goal: 初始目标
            final_goal: 最终目标
            max_steps: 最大步数
            
        Returns:
            测试报告
        """
        initial_goal = initial_goal or "启动游戏并登录"
        final_goal = final_goal or "打开背包界面"
        
        print("\n" + "="*60)
        print("🤖 智能游戏自动化测试（无人值守）")
        print("="*60)
        print(f"🎯 最终目标: {final_goal}")
        print(f"🔢 最大步数: {max_steps}")
        print("="*60 + "\n")
        
        start_time = time.time()
        current_goal = initial_goal
        self.step_count = 0
        
        while self.step_count < max_steps:
            self.step_count += 1
            print(f"\n📍 步骤 {self.step_count}/{max_steps} | 目标: {current_goal}")
            
            # 截图
            screenshot = self.controller.take_screenshot(f"step_{self.step_count:03d}")
            
            # AI 决策
            decision = self.vision.decide_action(screenshot, current_goal)
            
            # 执行
            action = decision.get("action", "wait")
            print(f"  🤖 决策: {action}")
            
            if action == "done":
                print("\n🎉 测试完成！")
                break
            
            elif action == "click":
                target = decision.get("target", "")
                x = decision.get("x")
                y = decision.get("y")
                
                if x and y:
                    self.controller.click(x, y)
                    print(f"  👆 点击: ({x}, {y}) - {target}")
                else:
                    # 让 AI 找位置
                    element = self.vision.find_element(screenshot, target)
                    if element.get("found"):
                        self.controller.click(element["x"], element["y"])
                        print(f"  👆 点击: ({element['x']}, {element['y']}) - {target}")
            
            elif action == "input":
                target = decision.get("target", "")
                value = decision.get("value", "")
                
                element = self.vision.find_element(screenshot, target)
                if element.get("found"):
                    self.controller.click(element["x"], element["y"])
                    time.sleep(0.3)
                    self.controller.input_chinese(value)
                    print(f"  ⌨️ 输入: {value}")
            
            elif action == "wait":
                seconds = decision.get("seconds", 2)
                self.controller.wait(seconds)
                print(f"  ⏳ 等待: {seconds}s")
            
            # 更新目标
            next_goal = decision.get("next_goal")
            if next_goal:
                current_goal = next_goal
            
            # 检查最终目标
            if final_goal in current_goal:
                time.sleep(2)
                verify = self.vision.verify_state(screenshot, final_goal)
                if verify.get("matched"):
                    print(f"\n🎉 最终目标达成: {final_goal}")
                    break
            
            time.sleep(1)
        
        duration = time.time() - start_time
        
        report = {
            "success": True,
            "steps": self.step_count,
            "duration": f"{duration:.1f}s"
        }
        
        print("\n" + "="*60)
        print("📊 测试报告")
        print("="*60)
        print(f"✅ 完成")
        print(f"🔢 步数: {self.step_count}")
        print(f"⏱️ 耗时: {report['duration']}")
        print("="*60)
        
        return report


def run_test():
    """快捷测试入口"""
    tester = AutoGameTester()
    return tester.run()


if __name__ == "__main__":
    run_test()
