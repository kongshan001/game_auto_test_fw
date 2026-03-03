# -*- coding: utf-8 -*-
"""
智能游戏自动化测试器 - 完全无人值守

基于 GLM-4.6V 多模态模型，实现真正的智能自动化测试
"""

import time
import json
from pathlib import Path
from typing import Optional, Dict, Any, List

from .glm_vision import GLMVision
from .game_controller import GameController

import sys
sys.path.append(str(Path(__file__).parent.parent))
import config


class AutoGameTester:
    """
    智能游戏自动化测试器
    
    特点:
    - 完全无人值守
    - AI 自主决策
    - 目标驱动
    - 支持深度思考
    """
    
    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        thinking: bool = None
    ):
        """
        初始化测试器
        
        Args:
            api_key: GLM API Key (默认从 config 读取)
            model: 模型名称 (默认从 config 读取)
            thinking: 是否开启深度思考 (默认从 config 读取)
        """
        self.vision = GLMVision(
            api_key=api_key or config.GLM_API_KEY,
            model=model or config.GLM_MODEL
        )
        self.controller = GameController()
        
        self.thinking = thinking if thinking is not None else config.GLM_THINKING
        self.step_count = 0
        self.history: List[Dict] = []
    
    def run(
        self,
        initial_goal: str = None,
        final_goal: str = None,
        max_steps: int = None,
        on_step: callable = None
    ) -> Dict[str, Any]:
        """
        运行自动化测试
        
        Args:
            initial_goal: 初始目标
            final_goal: 最终目标
            max_steps: 最大步数
            on_step: 每步回调函数
        
        Returns:
            测试报告
        """
        initial_goal = initial_goal or config.TEST_GOALS.get("initial", "启动游戏并登录")
        final_goal = final_goal or config.TEST_GOALS.get("final", "完成测试")
        max_steps = max_steps or config.MAX_STEPS
        
        print("\n" + "=" * 60)
        print("🤖 GLM 智能游戏自动化测试")
        print("   完全无人值守 · 自主决策 · 多模态识别")
        print("=" * 60)
        print(f"🎯 最终目标: {final_goal}")
        print(f"🔢 最大步数: {max_steps}")
        print(f"🧠 深度思考: {'开启' if self.thinking else '关闭'}")
        print(f"📦 模型: {self.vision.model}")
        print("=" * 60 + "\n")
        
        start_time = time.time()
        current_goal = initial_goal
        self.step_count = 0
        self.history = []
        
        while self.step_count < max_steps:
            self.step_count += 1
            
            print(f"\n📍 步骤 {self.step_count}/{max_steps}")
            print(f"   🎯 当前目标: {current_goal}")
            
            # 截图
            screenshot = self.controller.take_screenshot(f"step_{self.step_count:03d}")
            
            # AI 决策
            context = self._build_context()
            decision = self.vision.decide_action(
                image_path=screenshot,
                goal=current_goal,
                context=context
            )
            
            # 记录历史
            step_record = {
                "step": self.step_count,
                "goal": current_goal,
                "screenshot": screenshot,
                "decision": decision
            }
            self.history.append(step_record)
            
            # 执行决策
            action = decision.get("action", "wait")
            print(f"   🤖 决策: {action}")
            
            result = self._execute_action(decision, screenshot)
            step_record["result"] = result
            
            # 回调
            if on_step:
                on_step(step_record)
            
            # 检查完成
            if action == "done":
                print("\n🎉 测试完成！目标已达成")
                break
            
            if action == "fail":
                print("\n❌ 测试失败，需要人工介入")
                break
            
            # 更新目标
            next_goal = decision.get("next_goal")
            if next_goal:
                current_goal = next_goal
                print(f"   ➡️ 下一目标: {current_goal}")
            
            # 验证最终目标
            if self._check_final_goal(screenshot, final_goal):
                print(f"\n🎉 最终目标达成: {final_goal}")
                break
            
            # 等待
            time.sleep(config.ACTION_DELAY)
        
        duration = time.time() - start_time
        
        report = {
            "success": self.step_count < max_steps,
            "steps": self.step_count,
            "duration": round(duration, 1),
            "final_goal": final_goal,
            "model": self.vision.model,
            "history": self.history
        }
        
        self._print_summary(report)
        
        return report
    
    def _build_context(self) -> str:
        """构建上下文信息"""
        if not self.history:
            return None
        
        # 最近 3 步历史
        recent = self.history[-3:]
        actions = [f"步骤{h['step']}: {h['decision'].get('action')}" for h in recent]
        return "最近操作: " + " → ".join(actions)
    
    def _execute_action(self, decision: Dict, screenshot: str) -> Dict:
        """执行决策动作"""
        action = decision.get("action")
        result = {"action": action, "success": False}
        
        try:
            if action == "click":
                x = decision.get("x")
                y = decision.get("y")
                target = decision.get("target", "")
                
                if x and y:
                    self.controller.click(x, y)
                    print(f"   👆 点击: ({x}, {y}) - {target}")
                    result["success"] = True
                else:
                    # 让 AI 找位置
                    element = self.vision.find_element(screenshot, target)
                    if element.get("found"):
                        self.controller.click(element["x"], element["y"])
                        print(f"   👆 点击: ({element['x']}, {element['y']}) - {target}")
                        result["success"] = True
                    else:
                        print(f"   ⚠️ 未找到元素: {target}")
            
            elif action == "input":
                target = decision.get("target", "")
                text = decision.get("text", decision.get("value", ""))
                
                element = self.vision.find_element(screenshot, target)
                if element.get("found"):
                    self.controller.click(element["x"], element["y"])
                    time.sleep(0.3)
                    self.controller.input_chinese(text)
                    print(f"   ⌨️ 输入: {text}")
                    result["success"] = True
                else:
                    print(f"   ⚠️ 未找到输入框: {target}")
            
            elif action == "swipe":
                direction = decision.get("direction", "up")
                self.controller.swipe(direction)
                print(f"   👆 滑动: {direction}")
                result["success"] = True
            
            elif action == "wait":
                seconds = decision.get("seconds", 2)
                self.controller.wait(seconds)
                print(f"   ⏳ 等待: {seconds}s")
                result["success"] = True
        
        except Exception as e:
            result["error"] = str(e)
            print(f"   ❌ 执行失败: {e}")
        
        return result
    
    def _check_final_goal(self, screenshot: str, final_goal: str) -> bool:
        """检查是否达成最终目标"""
        verify = self.vision.verify_state(screenshot, final_goal)
        if verify.get("matched") and verify.get("confidence", 0) > 0.8:
            return True
        return False
    
    def _print_summary(self, report: Dict):
        """打印测试摘要"""
        print("\n" + "=" * 60)
        print("📊 测试报告")
        print("=" * 60)
        status = "✅ 成功" if report["success"] else "❌ 失败"
        print(f"状态: {status}")
        print(f"步数: {report['steps']}")
        print(f"耗时: {report['duration']}s")
        print(f"模型: {report['model']}")
        print("=" * 60)


def run_test(
    initial_goal: str = None,
    final_goal: str = None,
    max_steps: int = None
) -> Dict:
    """快捷测试入口"""
    tester = AutoGameTester()
    return tester.run(
        initial_goal=initial_goal,
        final_goal=final_goal,
        max_steps=max_steps
    )


if __name__ == "__main__":
    run_test()
