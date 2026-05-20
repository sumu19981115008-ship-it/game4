# game4 项目架构文档

## 项目基本信息

| 项目 | 内容 |
|------|------|
| 项目名称 | 宝可梦传说 Z-A 同人版（Pokemon Legends ZA Fan） |
| 引擎 | Godot 4.6.2 / GDScript |
| 开发方式 | AI全程编写代码，人工测试反馈 |
| 本地路径 | D:/fixelflow/game4/ |
| 当前版本 | v0.1.0 |
| 游戏类型 | 俯视角2D像素RPG |
| 基准分辨率 | 320×180（Camera2D zoom×2 → 640×360 → 窗口拉伸至1280×720） |

---

## 整体架构

```
输入系统（InputMap）
    └──> Player（CharacterBody2D）──> PlayerCamera（Camera2D）
              │
              ├──> CollisionSystem（wall/npc/trigger/wild_zone）
              ├──> TriggerSystem（ZoneTransition / StoryTrigger）
              │         ├──> MapSystem（ProceduralMap / TileMapLayer）
              │         └──> BattleSystem（BattleStateMachine）
              └──> SaveManager（检查点存档）

EventBus（Autoload）──> 跨系统信号广播
FlagManager（Autoload）──> 剧情标记与条件判断
```

---

## 目录结构

```
game4/
├── project.godot                # Godot项目配置（输入映射/碰撞层/Autoload注册）
├── ARCHITECTURE.md              # 本文档
├── CHANGELOG.md                 # 版本更新日志
│
├── autoloads/                   # 全局单例（Autoload），按依赖顺序加载
│   ├── EventBus.gd              # 全局信号总线（跨系统通信）
│   ├── FlagManager.gd           # 剧情标记管理（持久化/条件表达式）
│   ├── WorldStateManager.gd     # 世界状态（区域解锁/危机等级/天气时间）
│   ├── SaveManager.gd           # 存档系统（3槽手动 + 1槽自动）
│   ├── PokemonDatabase.gd       # 宝可梦图鉴数据库（.tres资源缓存）
│   ├── MoveDatabase.gd          # 技能数据库
│   ├── DialogueManager.gd       # 对话系统（JSON节点式）
│   ├── AudioManager.gd          # 音频管理（BGM淡入淡出/SFX）
│   ├── TransitionManager.gd     # 场景过渡（淡入淡出/白闪）
│   └── SettingsManager.gd       # 游戏设置（音量/全屏/语言）
│
├── scripts/
│   ├── globals/
│   │   └── CollisionLayers.gd   # 碰撞层常量（Autoload）
│   ├── player/
│   │   ├── Player.gd            # 玩家角色（CharacterBody2D，8方向移动）
│   │   └── PlayerCamera.gd      # 相机（跟随平滑/边界限制/剧情锁定）
│   ├── world/
│   │   ├── ProceduralMap.gd     # 程序化地图生成器（开发期临时，待替换为TileMap）
│   │   ├── ZoneTransition.gd    # 区域切换触发器（无缝/淡入/加载三种模式）
│   │   ├── StoryTrigger.gd      # 剧情触发器（条件判断/单次触发）
│   │   └── zones/
│   │       └── TestZone.gd      # 测试地图脚本
│   ├── battle/
│   │   ├── BattleStateMachine.gd  # 回合制战斗状态机（8阶段）
│   │   └── BattleCalculator.gd    # 伤害/命中/逃跑公式（静态方法）
│   ├── pokemon/
│   │   └── PokemonInstance.gd   # 宝可梦实例（能力值计算/战斗临时状态）
│   ├── systems/
│   │   ├── capture/
│   │   │   └── CaptureSystem.gd   # 第六世代捕捉公式
│   │   └── mega/
│   │       └── MegaEvolutionSystem.gd  # 超级进化（每场战斗限一次）
│   ├── utils/
│   │   └── TypeChart.gd         # 18×18属性相克表（静态查询）
│   ├── main/
│   │   └── Main.gd              # 启动脚本（初始化存档目录→跳转场景）
│   └── network/
│       └── NetworkManager.gd    # 联机预留框架（当前全部为stub）
│
├── data/
│   ├── enums/
│   │   └── PokemonEnums.gd      # 枚举定义（属性/状态/性格/战斗结果/方向）
│   ├── species/
│   │   ├── PokemonSpeciesData.gd  # 宝可梦图鉴Resource定义
│   │   └── db/                  # .tres静态数据文件（待填充）
│   ├── moves/
│   │   └── MoveData.gd          # 技能Resource定义
│   └── natures/
│       └── NatureTable.gd       # 25性格修正表
│
├── scenes/
│   ├── main/
│   │   └── Main.tscn            # 项目入口场景
│   ├── entities/
│   │   └── player/
│   │       └── Player.tscn      # 玩家场景（CharacterBody2D + 碰撞体 + Camera）
│   └── world/
│       └── zones/
│           └── TestZone.tscn    # 测试地图场景（程序化生成）
│
├── assets/                      # 美术/音频资源（待填充）
│   ├── sprites/                 # 精灵图（宝可梦/角色/NPC）
│   ├── tilesets/                # 地图图块集
│   ├── ui/                      # UI图集/字体
│   ├── audio/                   # BGM/SFX
│   └── shaders/                 # 着色器
│
└── .ai_dev/                     # AI开发专用文件夹
    ├── README.md                # 使用说明
    ├── CURRENT_STATE.md         # 当前开发状态
    ├── architecture/            # 架构决策记录（ADR）
    ├── logs/                    # 每次开发session日志
    └── assets_registry/         # 美术资源登记表
```

---

## Autoload 加载顺序与职责

| 顺序 | 名称 | 职责 | 依赖 |
|------|------|------|------|
| 1 | EventBus | 全局信号总线 | 无 |
| 2 | FlagManager | 剧情标记 | EventBus |
| 3 | WorldStateManager | 世界状态 | EventBus, FlagManager |
| 4 | SaveManager | 存档读写 | FlagManager, WorldStateManager |
| 5 | PokemonDatabase | 宝可梦数据 | 无 |
| 6 | MoveDatabase | 技能数据 | 无 |
| 7 | DialogueManager | 对话系统 | EventBus, FlagManager |
| 8 | AudioManager | 音频 | 无 |
| 9 | TransitionManager | 场景过渡 | 无 |
| 10 | SettingsManager | 设置 | AudioManager |
| 11 | CollisionLayers | 碰撞层常量 | 无 |
| 12 | NetworkManager | 联机预留 | EventBus |

---

## 碰撞层系统

| 层编号 | 名称 | 值（位掩码） | 使用对象 |
|--------|------|------------|---------|
| Layer 1 | player | 1 | 玩家 CharacterBody2D |
| Layer 2 | npc | 2 | NPC CharacterBody2D |
| Layer 3 | wall | 4 | 墙壁/障碍 TileMapLayer |
| Layer 4 | trigger | 8 | 触发区域 Area2D |
| Layer 5 | wild_zone | 16 | 野生宝可梦区域 Area2D |
| Layer 6 | item | 32 | 场景拾取物 Area2D |
| Layer 7 | projectile | 64 | 投射物（预留） |
| Layer 8 | camera_zone | 128 | 相机边界辅助 Area2D |

**Player碰撞配置**：collision_layer=1，collision_mask=190（NPC+WALL+TRIGGER+WILD_ZONE+ITEM+CAMERA_ZONE）

---

## 战斗状态机（8阶段）

```
INTRO → PLAYER_INPUT → ENEMY_THINK → ORDER_RESOLVE
    → EXECUTE_ACTION → END_OF_TURN → CHECK_FAINT → BATTLE_END
```

伤害公式采用官方第六世代标准：
`floor(floor(2*level/5+2) * power * atk/def / 50 + 2) * modifiers`

---

## 存档系统

- 路径：`user://saves/`（Windows: `%APPDATA%/Godot/app_userdata/Pokemon Legends ZA Fan/`）
- 格式：JSON，含版本号字段
- 槽位：3个手动槽（save_slot_0~2.json）+ 1个自动槽（autosave.json）+ 元信息（save_meta.json）

---

## 联机预留设计

`NetworkManager.gd` 当前为全stub框架，所有方法调用时输出警告。
未来实现时需要替换的关键点：
- `host_game()` / `join_game()`：ENet 或 WebRTC 连接建立
- `broadcast_battle_action(action: Dictionary)`：RPC广播战斗指令
- `sync_player_position(position: Vector2)`：MultiplayerSynchronizer 位置同步
- `BattleCalculator` 已设计为纯静态方法，便于迁移至服务端执行

---

## 开发规范

- 所有注释、提交信息、变量自然语言描述使用**中文**
- 场景文件（.tscn）通过代码或编辑器维护，不手写
- 美术资源替换时不改动脚本逻辑，通过场景节点引用解耦
- AI开发日志保存至 `.ai_dev/logs/`，格式：`YYYY-MM-DD_任务名.md`
- 每次开发结束更新 `.ai_dev/CURRENT_STATE.md`
