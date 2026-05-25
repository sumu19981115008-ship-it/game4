# game4 — Claude Code 操作手册

## 启动协议（每次新窗口必须执行）

按顺序读取以下文件，建立完整上下文：

1. 读取 `HANDOFF.md` — 上一个窗口的交接信息（最重要）
2. 读取 `.ai_dev/CURRENT_STATE.md` — 当前任务状态和完成清单
3. 读取 `.ai_dev/architecture/ADR_001.md` — 已做的关键技术决策
4. 读取 `ARCHITECTURE.md` — 整体架构概览

读取完毕后，主动汇报："我已了解项目状态，当前是 [摘要]，准备继续 [任务]。"

---

## 项目结构说明

```
game4/
├── CLAUDE.md                    ← 本文件，AI 操作手册
├── HANDOFF.md                   ← 会话交接便签（每次覆盖）
├── CHANGELOG.md                 ← 变更日志（只增不改）
├── ARCHITECTURE.md              ← 架构概览（按需更新）
│
├── .ai_dev/                     ← AI 开发管理层（核心）
│   ├── CURRENT_STATE.md         ← 当前任务状态（每次更新）
│   ├── architecture/            ← 技术决策与架构文档
│   │   ├── ADR_001.md           ← 技术决策记录（只增不改）
│   │   └── GBA_地图渲染技术手册.md
│   ├── logs/                    ← 每日开发日志（按日期追加）
│   └── assets_registry/
│       └── ASSETS.md            ← 资产清单（按需更新）
│
├── docs/策划案/                  ← 游戏设计文档（稳定参考）
│   ├── 01_游戏概述与世界观.md
│   ├── 02_核心玩法系统.md
│   ├── 03_战斗系统设计.md
│   ├── 04_地图与世界结构.md
│   ├── 05_宝可梦图鉴与成长系统.md
│   └── 06_NPC与对话系统.md
│
├── tools/                       ← 地图渲染 Python 工具
└── assets/                      ← 美术资源
```

---

## 关闭协议（每次窗口结束前必须执行）

1. **覆盖 `HANDOFF.md`** — 写明：做了什么 / 下一步做什么（按优先级） / 重要上下文和注意事项 / 未完成的半成品
2. **更新 `.ai_dev/CURRENT_STATE.md`** — 更新完成清单和当前阶段描述
3. **追加 `CHANGELOG.md`** — 格式：`## [YYYY-MM-DD] Session N\n- 做了什么`
4. **按需追加 `.ai_dev/architecture/ADR_001.md`** — 如果做了新的技术决策
5. **执行 git 提交并推送**：
   ```bash
   git add HANDOFF.md CHANGELOG.md ARCHITECTURE.md .ai_dev/
   git commit -m "session 交接：[一句话摘要本次做了什么]"
   git push origin master
   ```

### 保底机制（任何步骤出错时强制执行）

- 步骤 1-4 任意一步写入失败 → 立即停止，报告"[步骤名] 写入失败：[具体错误]"，**等待用户指令**
- `git commit` 失败（如冲突、权限问题）→ 报告错误原因，列出未提交的文件清单，**等待用户指令**
- `git push` 失败（如网络异常、远端拒绝）→ 报告"本地已保存，推送失败：[原因]"，**等待用户指令**
- **在用户明确说"可以关闭"之前，不得宣布交接完毕**

正常完成时说："交接完毕，已推送至 GitHub，下一个窗口可以继续。是否关闭？"
用户确认后才结束。

---

## Vault 行为规则

### 可以做的
- 读取和修改 `.ai_dev/` 下所有文件
- 更新 `HANDOFF.md` / `CHANGELOG.md` / `ARCHITECTURE.md`
- 在 `docs/` 下新增设计文档
- 在 `.ai_dev/logs/` 下新建或追加日志文件
- 在 `tools/` 下新建地图渲染工具脚本

### 不可以做的
- 不能删除 `CHANGELOG.md` 和 `ADR_001.md` 中的已有内容（只能追加）
- 不能修改 `docs/策划案/` 中已确认的设计文档（除非用户明确要求）
- 不能跳过启动协议直接开始干活

---

## 遇到技术分叉时

在 `.ai_dev/architecture/ADR_001.md` 中追加新的 ADR 条目（编号递增），记录分叉点和可选方案，等用户确认后再执行。格式：

```
## ADR-XXX：[决策标题]
- **日期**：YYYY-MM-DD
- **背景**：[为什么面临这个决策]
- **选项**：
  - 选项A：[描述] — 优点 / 缺点
  - 选项B：[描述] — 优点 / 缺点
- **决策**：[选了什么]
- **原因**：[为什么]
```

---

## 远端参考资料

- **GitHub 仓库**：`https://github.com/sumu19981115008-ship-it/game4.git`（master 分支）
- 技术文档、架构文档均已纳入版本控制
- 如需查看远端状态：`git log --oneline -10`

---

## 任务优先级

- **P0（阻塞）** — 影响其他所有任务，立刻处理
- **P1（当前迭代）** — 必须在这个阶段完成
- **P2（计划中）** — 排期内的任务
- **P3（待定）** — 有想法但未排期

---

## 项目关键信息速查

- **引擎**：Godot 4.6.2 / GDScript
- **当前版本**：v0.1.0（~40% 完成）
- **Autoload 单例**：EventBus / SaveManager / FlagManager / WorldStateManager / PokemonDatabase / MoveDatabase / DialogueManager / AudioManager / TransitionManager / SettingsManager / CollisionLayers / NetworkManager
- **已有地图**：LittlerootTown / Route101 / OldaleTown / StarterVillage / RouteForest / NovaTown
- **运行方式**：Godot 4.6 打开 `project.godot`，F5 运行，WASD 移动，Shift 奔跑
