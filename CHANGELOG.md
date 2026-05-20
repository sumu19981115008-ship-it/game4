# 开发更新日志

## v0.1.0 — 2026-05-20 — 底层架构搭建 + 首个可运行场景

### 新增

- **项目结构**：完整目录骨架（autoloads/scripts/data/scenes/assets/.ai_dev），91个目录
- **Autoload单例系统**：12个全局单例按依赖顺序注册
  - EventBus（全局信号总线，28个跨系统信号）
  - FlagManager（剧情标记，支持AND/OR/NOT条件表达式）
  - WorldStateManager（区域解锁/危机等级/天气时间）
  - SaveManager（3槽手动存档 + 自动存档，JSON格式）
  - PokemonDatabase / MoveDatabase（.tres资源缓存）
  - DialogueManager（JSON节点式对话，暂停游戏树）
  - AudioManager（BGM淡入淡出/SFX，动态创建子节点）
  - TransitionManager（淡黑/白闪场景过渡）
  - SettingsManager（ConfigFile持久化设置）
  - CollisionLayers（碰撞层位掩码常量）
  - NetworkManager（联机预留框架，全stub）
- **数据层**：PokemonEnums（18属性/8状态/6成长/4方向）、PokemonSpeciesData（Resource定义）、MoveData、NatureTable（25性格修正表）、TypeChart（18×18属性相克完整表）
- **玩家系统**：Player.gd（CharacterBody2D，8方向移动，acceleration/friction手感参数）、PlayerCamera.gd（平滑跟随/边界限制/剧情锁定解锁）
- **世界系统**：ZoneTransition.gd（SEAMLESS/FADE/LOAD三种切换）、StoryTrigger.gd（条件触发/单次触发）
- **战斗框架**：BattleStateMachine.gd（8阶段状态机）、BattleCalculator.gd（官方伤害/命中/逃跑/急所公式）、CaptureSystem.gd（第六世代捕捉公式）、MegaEvolutionSystem.gd（超级进化，每场限一次）
- **场景文件**：Main.tscn（入口）、Player.tscn（角色场景）、TestZone.tscn（测试地图）
- **程序化地图**：ProceduralMap.gd，代码生成40×25格地图，含地面/小路/建筑/水池，StaticBody2D合并碰撞体
- **AI开发文档**：.ai_dev/README.md、CURRENT_STATE.md、架构ADR、开发日志

### 修复（开发期bug修正）

- `SaveManager.get_meta()` 与 Godot Object基类内置方法同名冲突 → 改名为 `get_save_meta()`
- `AudioManager` 使用 `@onready` 引用尚未创建的子节点 → 改为普通变量在 `_ready()` 中赋值
- `CollisionLayers` 同时有 `class_name` 和 Autoload 名称冲突 → 删除 `class_name`，改为 `extends Node`
- `NatureTable` / `SettingsManager` / `FlagManager` / `BattleCalculator` 中 `:=` 无法推断 Variant 类型 → 显式声明类型
- `Main.gd` 在 `_ready()` 中直接调用 `change_scene_to_file` 导致父节点忙碌报错 → 改为 `call_deferred`
- `Player.gd` AnimatedSprite2D 无动画帧时每帧报错刷屏 → 增加 `sprite_frames` 存在性检查
- `PokemonEnums.Direction` 在 Player 信号中引用导致循环依赖风险 → 简化为 int 类型

### 已知待处理

- AnimatedSprite2D 无真实动画帧，玩家无精灵图（用ColorRect临时替代）
- TileMapLayer 为空，地图由 ProceduralMap 程序生成（待替换为真实美术素材）
- BattleCalculator 内部 TYPE_CHART 为简化版，需与 TypeChart.gd 统一
- 美术资源全部缺失（宝可梦精灵/地图图块/UI图集/字体）
