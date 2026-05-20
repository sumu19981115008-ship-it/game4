# 开发交接文档

**交接时间**：2026-05-20  
**当前版本**：v0.1.0  
**接手时第一件事**：阅读本文档 + `ARCHITECTURE.md` + `.ai_dev/CURRENT_STATE.md`

---

## 项目现状一句话总结

底层架构已完成，游戏可以运行——玩家能在程序化生成的测试地图上移动，碰撞系统正常。**下一阶段核心任务是引入美术资源，把测试场景替换为真实画面。**

---

## 立即可运行

用 Godot 4.6 打开 `D:\fixelflow\game4\project.godot`，按 F5，工具栏点亮「输入」按钮，WASD 移动，Shift 奔跑。

---

## 美术资源（最优先任务）

### 当前占位状态

| 资源类型 | 当前状态 | 占位方案 |
|---------|---------|---------|
| 玩家精灵 | ❌ 无 | ColorRect 红色方块 |
| 地图图块 | ❌ 无 | ProceduralMap 程序色块 |
| 宝可梦精灵 | ❌ 无 | 无 |
| UI 图集 | ❌ 无 | 无 |
| 字体 | ❌ 无 | Godot 默认字体 |
| BGM/SFX | ❌ 无 | 无 |

### 推荐素材来源

#### 地图图块集（最优先）

**The Spriters Resource** — `www.spriters-resource.com`
- 搜索：`Pokemon X Y Tilesets` 或 `Pokemon Omega Ruby Tilesets`
- X/Y 系列图块 16×16 像素，与本项目完全匹配
- 免费下载，任天堂同人默认不追究（不可商用）

**替代方案**：itch.io 搜索 `pokemon tileset free`，有社区制作的开源版本

#### 宝可梦精灵图

**The Spriters Resource**
- 搜索：`Pokemon X Y Pokemon Sprites`（正面/背面战斗精灵，约80×80px）
- 搜索：`Pokemon X Y Overworld`（俯视角行走精灵，约32×32px 4方向8帧）

#### 玩家角色精灵

**The Spriters Resource**
- 搜索：`Pokemon Legends Arceus Player`（最接近本作风格）
- 或用 X/Y 主角精灵替代（Calem/Serena）
- 需要：上下左右4方向 × 待机/行走/奔跑 = 12套动画

#### 字体（免费商用）

| 字体 | 用途 | 下载 |
|------|------|------|
| DotGothic16 | 主要 UI 文字（中文支持） | Google Fonts 搜索 DotGothic16 |
| m5x7 | 英文标题/数字 | itch.io 搜索 m5x7 |
| PixelMplus12 | 中文正文备用 | github.com/itouhiro/PixelMplus |

### 资源放置规范

```
assets/
├── sprites/
│   ├── pokemon/
│   │   ├── front/          # 战斗正面精灵：001_bulbasaur.png ...
│   │   ├── back/           # 战斗背面精灵
│   │   ├── overworld/      # 俯视角行走：001_bulbasaur_walk.png
│   │   └── icons/          # 图鉴小图标（32×32）
│   ├── characters/
│   │   ├── player/         # 主角行走精灵表（spritesheet）
│   │   └── npcs/           # NPC 精灵
│   └── maps/
│       └── tilesets/       # 地图图块集：lumiose_city.png（单张大图）
├── fonts/                  # .ttf / .otf 文件
└── audio/
    ├── bgm/                # .ogg 格式（Godot 推荐）
    └── sfx/
```

### 引入美术资源后需要做的工作

1. **图块集**：在 Godot 编辑器的 TileSet 面板中，导入图片后框选每个图块，为有碰撞的图块（墙壁/建筑）添加物理层
2. **玩家精灵**：在 Player.tscn 的 AnimatedSprite2D 节点上，新建 SpriteFrames 资源，按方向和动作添加帧
3. **替换 ProceduralMap**：当图块集配置完成后，将 TestZone.tscn 中的 ProceduralMap 节点替换为 TileMapLayer 节点，参照 `ARCHITECTURE.md` 的6层结构

---

## 当前代码结构关键文件

| 文件 | 作用 | 注意事项 |
|------|------|---------|
| `scripts/player/Player.gd` | 玩家移动逻辑 | 已简化信号类型为int，动画判断有sprite_frames保护 |
| `scripts/player/PlayerCamera.gd` | 相机跟随/边界 | zoom=2x，基准分辨率320×180 |
| `scripts/world/ProceduralMap.gd` | 临时程序化地图 | 将来替换为TileMap时删除此文件 |
| `autoloads/EventBus.gd` | 全局信号总线 | 所有跨系统通信走这里 |
| `autoloads/SaveManager.gd` | 存档系统 | 注意：方法名是get_save_meta()不是get_meta() |
| `autoloads/AudioManager.gd` | 音频 | bgm_player/sfx_player是普通变量，不是@onready |
| `scripts/globals/CollisionLayers.gd` | 碰撞层常量 | extends Node（无class_name，避免与Autoload名冲突） |

---

## 已知问题 / 踩坑记录

1. **Godot 4.6 类型推断收紧**：`:=` 无法从 `Array/PackedStringArray` 等 Variant 子类推断，必须显式写类型（如 `var x: PackedStringArray = ...`）
2. **Autoload 与 class_name 不能同名**：如果脚本注册为 Autoload `Foo`，就不能再写 `class_name Foo`
3. **`_ready()` 中不能直接调用 `change_scene_to_file`**：必须用 `call_deferred`
4. **编辑器工具栏「输入」按钮**：每次 F5 运行后必须点亮，否则游戏收不到键盘输入
5. **`@onready` 与动态 `add_child`**：`@onready` 在 `_ready()` 执行前赋值，如果节点是在 `_ready()` 里才创建的，`@onready` 会拿到 null

---

## 下一步开发优先级

1. **【美术】** 获取地图图块集并在编辑器配置 TileSet 碰撞
2. **【美术】** 获取玩家行走精灵并配置 AnimatedSprite2D 动画帧
3. **【功能】** 对话框 UI（DialogueBox.tscn，CanvasLayer layer=5）
4. **【功能】** HUD 场景（血量/等级/时间，layer=10）
5. **【数据】** 填充3只测试宝可梦 .tres 数据（小火龙/妙蛙种子/杰尼龟）
6. **【数据】** 填充5个测试技能 .tres 数据
7. **【修复】** BattleCalculator 内联 TYPE_CHART 与 TypeChart.gd 统一
