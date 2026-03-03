# -*- coding: utf-8 -*-
"""
主入口 - GLM 智能游戏自动化测试
完全无人值守，自主决策
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.auto_tester import AutoGameTester, run_test
from src.game_controller import GameController
from src.glm_vision import GLMVision

import config


def main():
    """主入口 - 智能自动化测试"""
    print("=" * 60)
    print("🤖 GLM 智能游戏自动化测试系统")
    print("   完全无人值守 · 自主决策 · 多模态识别")
    print("=" * 60)
    print(f"🎮 游戏: {config.GAME_NAME}")
    print(f"📁 路径: {config.GAME_EXE_PATH}")
    print(f"🧠 模型: {config.GLM_MODEL}")
    print("=" * 60)
    
    # 检查 API Key
    if config.GLM_API_KEY == "YOUR_API_KEY_HERE":
        print("\n⚠️ 请先配置 GLM API Key！")
        print("   编辑 config.py，设置 GLM_API_KEY")
        print("   获取地址: https://open.bigmodel.cn/")
        return
    
    # 初始化测试器
    tester = AutoGameTester()
    
    try:
        # 运行完全自动化测试
        report = run_test()
        
        # 保存报告
        save_report(report)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断测试")
    except Exception as e:
        print(f"\n\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()


def save_report(report: dict):
    """保存测试报告"""
    import json
    from datetime import datetime
    
    report_dir = Path("./reports")
    report_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = report_dir / f"test_report_{timestamp}.json"
    
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 报告已保存: {report_file}")


if __name__ == "__main__":
    main()
