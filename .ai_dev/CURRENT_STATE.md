# 当前开发状态

**最后更新**：2026-05-20（Session 2）  
**当前阶段**：基础场景已创建，可在 Godot 编辑器中运行测试  
**Godot 版本**：4.x（待确认具体版本）

---

## 已完成

- [x] 项目目录结构搭建
- [x] project.godot（含输入映射、碰撞层、渲染设置、Autoload注册）
- [x] 所有 Autoload 单例框架（EventBus / FlagManager / WorldStateManager / SaveManager / PokemonDatabase / MoveDatabase / DialogueManager / AudioManager / TransitionManager / SettingsManager）
- [x] 数据类定义（PokemonSpeciesData / LearnableMove / EvolutionCondition / MoveData / PokemonEnums / NatureTable）
- [x] PokemonInstance（含能力值计算公式）
- [x] Player.gd（8方向移动，加速/摩擦，动画状态机接口）
- [x] PlayerCamera.gd（平滑跟随，边界限制，锁定/解锁）
- [x] ZoneTransition.gd（三种切换模式）
- [x] StoryTrigger.gd（剧情触发器）
- [x] BattleStateMachine.gd（回合制状态机框架）
- [x] BattleCalculator.gd（伤害公式、属性相克、急所）
- [x] TypeChart.gd（完整18×18属性相克表）
- [x] CaptureSystem.gd（第六世代捕捉公式）
- [x] MegaEvolutionSystem.gd（超级进化触发/恢复）
- [x] CollisionLayers.gd（碰撞层常量）
- [x] NetworkManager.gd（联机预留框架）
- [x] Main.gd + Main.tscn（启动场景）
- [x] Player.tscn（CharacterBody2D + CapsuleShape2D + AnimatedSprite2D + PlayerCamera）
- [x] TestZone.gd + TestZone.tscn（测试地图，含玩家出生点和调试标签）

## 待完成（下一步）

- [ ] 在 Godot 编辑器中打开项目，验证 TestZone 可正常运行（玩家能移动）
- [ ] DialogueBox UI 场景（CanvasLayer layer=5）
- [ ] HUD 场景（血量/等级/时间）
- [ ] 填充至少3只宝可梦的测试数据（.tres文件，建议小火龙/妙蛙种子/杰尼龟）
- [ ] 填充至少5个技能的测试数据（.tres文件）
- [ ] 创建简单的 TileSet 测试地图（带有碰撞墙壁的地面图块）

## 已知问题 / 注意事项

- BattleCalculator 的 TYPE_CHART 已完整实现于 TypeChart.gd，但 BattleCalculator 内仍为简化版，两者需统一
- AudioManager 使用了 @onready，但节点在 _ready 中动态创建，需验证是否兼容
- 美术资源目前全为占位符，需等待素材确认后填充

## 美术资源状态

- 宝可梦精灵图：❌ 未获取
- 地图图块集：❌ 未获取
- UI 图集：❌ 未获取
- 字体：❌ 未下载（需要 PixelMplus12、m5x7、DotGothic16）
