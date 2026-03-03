# GLM 智能游戏自动化测试框架

基于智谱 GLM-4.6V 多模态大模型的完全无人值守游戏自动化测试框架。

## 特性

- 🧠 **GLM-4.6V 驱动** - 使用最新多模态视觉模型
- 🤖 **完全无人值守** - AI 自主决策，无需预设脚本
- 🎯 **目标驱动** - 描述目标，AI 自动规划执行
- 📸 **视觉理解** - 直接理解界面，无需坐标定位
- 🔄 **深度思考** - 支持开启 thinking 模式增强推理

## 项目结构

```
game-auto-test/
├── main.py              # 主入口
├── config.py            # 配置文件
├── requirements.txt     # Python 依赖
├── src/
│   ├── __init__.py
│   ├── auto_tester.py       # 智能测试器
│   ├── game_controller.py   # 游戏控制
│   └── glm_vision.py        # GLM-4.6V 视觉理解
├── screenshots/         # 截图目录
├── logs/               # 日志目录
└── reports/            # 测试报告
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置

编辑 `config.py` 或设置环境变量：

```bash
# 必填
export GLM_API_KEY="your-api-key"

# 可选
export GLM_MODEL="glm-4.6v-flash"  # 免费版
export GAME_NAME="YourGame"
export GAME_EXE_PATH="/path/to/game.exe"
```

### 3. 运行

```bash
python main.py
```

## 模型选择

| 模型 | 说明 | 适用场景 |
|------|------|----------|
| `glm-4.6v-flash` | 完全免费 | 测试、开发 |
| `glm-4.6v-flashx` | 轻量高速 | 生产环境 |
| `glm-4.6v` | 旗舰版 (106B) | 复杂场景 |

## API 文档

- [GLM-4.6V 官方文档](https://docs.bigmodel.cn/cn/guide/models/vlm/glm-4.6v)
- [获取 API Key](https://open.bigmodel.cn/)

## 工作原理

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   截图      │ ──▶ │  GLM-4.6V   │ ──▶ │   决策      │
│  Screenshot │     │  视觉理解   │     │  Decision   │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                                              ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   循环      │ ◀── │   执行      │ ◀── │  click/     │
│   Loop      │     │   Execute   │     │  input/wait │
└─────────────┘     └─────────────┘     └─────────────┘
```

1. **截图** - 捕获当前游戏界面
2. **理解** - GLM-4.6V 分析界面内容
3. **决策** - 基于目标决定下一步操作
4. **执行** - 执行点击/输入/等待等操作
5. **循环** - 直到目标完成或达到最大步数

## 测试流程示例

```python
from src.auto_tester import AutoGameTester

tester = AutoGameTester()
report = tester.run(
    initial_goal="启动游戏并登录",
    final_goal="打开背包界面",
    max_steps=30
)
print(report)
```

## License

MIT
