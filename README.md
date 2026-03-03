# GLM 游戏自动化测试系统

基于 GLM-4V 多模态大模型的游戏自动化测试框架

## 项目结构

```
game-auto-test/
├── main.py              # 主入口
├── config.py            # 配置文件（API Key、游戏路径）
├── requirements.txt     # Python 依赖
├── src/
│   ├── __init__.py
│   ├── game_controller.py   # 游戏控制（启动、截图、操作）
│   ├── glm_vision.py        # GLM-4V 视觉理解
│   ├── test_flow.py         # 测试流程编排
│   └── utils.py             # 工具函数
└── screenshots/         # 截图保存目录
```

## 测试流程

```
启动游戏 → 登录 → 选角色 → 进地图 → 打开背包 ✅
```

## 依赖

```bash
pip install -r requirements.txt
```

## 使用

1. 修改 `config.py` 填入 API Key 和游戏路径
2. 运行 `python main.py`
