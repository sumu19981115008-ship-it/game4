# AI 开发记录中心

本文件夹专供 AI 开发助手使用，记录每次开发会话的内容、决策和状态。

## 文件夹结构

```
.ai_dev/
├── README.md              ← 本文件，说明规范
├── CURRENT_STATE.md       ← 当前开发状态（每次开发后更新）
├── logs/                  ← 每次开发会话的记录
│   └── YYYY-MM-DD_描述.md
├── architecture/          ← 架构决策记录（ADR）
│   └── ADR_001_架构搭建.md
└── assets_registry/       ← 美术资源登记表
    └── ASSETS.md
```

## 使用规范

1. **每次开发会话开始前**：阅读 `CURRENT_STATE.md` 了解当前状态
2. **每次开发会话结束后**：
   - 更新 `CURRENT_STATE.md`
   - 在 `logs/` 下新建当日记录文件
3. **重大架构决策**：在 `architecture/` 下记录 ADR
4. **新增美术资源**：在 `assets_registry/ASSETS.md` 登记

## 开发优先级

1. ✅ 架构搭建（当前）
2. ⬜ 核心移动系统（Player + Camera）
3. ⬜ 地图系统（TileMap + 区域切换）
4. ⬜ 对话系统（DialogueBox UI）
5. ⬜ 宝可梦数据填充（测试用少量数据）
6. ⬜ 战斗系统（回合制核心）
7. ⬜ 捕捉 / 队伍 / 图鉴
8. ⬜ 剧情章节接入
9. ⬜ 完整 UI 润色
10. ⬜ 联机系统（NetworkManager 填充实现）
