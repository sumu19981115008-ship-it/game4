# 当前开发状态

**最后更新**：2026-05-20（Session 5）  
**当前阶段**：美术资源填充完成，玩家精灵已替换，存在行走动画帧错位待修  
**Godot 版本**：4.6.2.stable

---

## 已完成

- [x] 项目目录结构搭建
- [x] project.godot（含输入映射、碰撞层、渲染设置、Autoload注册）
- [x] 所有 Autoload 单例框架（EventBus / FlagManager / WorldStateManager / SaveManager / PokemonDatabase / MoveDatabase / DialogueManager / AudioManager / TransitionManager / SettingsManager）
- [x] 数据类定义（PokemonSpeciesData / LearnableMove / EvolutionCondition / MoveData / PokemonEnums / NatureTable）
- [x] PokemonInstance（含能力值计算公式）
- [x] Player.gd（8方向移动，加速/摩擦，动画状态机接入）
- [x] PlayerCamera.gd（平滑跟随，边界限制，锁定/解锁）
- [x] ZoneTransition.gd / StoryTrigger.gd
- [x] BattleStateMachine.gd / BattleCalculator.gd（属性相克委托 TypeChart）
- [x] TypeChart.gd（完整18×18属性相克表）
- [x] CaptureSystem.gd / MegaEvolutionSystem.gd
- [x] CollisionLayers.gd / NetworkManager.gd
- [x] Main.gd + Main.tscn / Player.tscn / TestZone.tscn
- [x] DialogueBox.tscn + HUD.tscn（已接入 TestZone）
- [x] 宝可梦静态精灵图（16只，front/back/shiny_front）
- [x] 战斗动画精灵表（19只 × 3变体，Showdown GIF 拆帧）
- [x] PokemonDatabase 精灵图接口（get_sprite_texture / get_anim_frames）
- [x] 宝可梦数据 .tres（妙蛙种子/小火龙/杰尼龟）
- [x] 技能数据 .tres（撞击/火焰喷射/水枪/藤鞭/催眠术）
- [x] 玩家精灵替换为绿宝石 Brendan GBA 原版像素图

## 待完成（下一步）

- [ ] **【Bug】玩家行走动画帧错位**（最优先）— 详见下方已知问题
- [ ] 地图图块集配置（TileSet 碰撞），替换 ProceduralMap
- [ ] 战斗场景 UI（按 03_战斗系统策划案 布局）
- [ ] HUD 按 05_UI_UX策划案 重做视觉（深夜蓝配色、卢米奥金边框）
- [ ] 填充更多宝可梦 .tres 数据

## 已知问题

### 🐛 玩家行走动画帧错位（高优先级）

**现象**：WASD 移动时人物像在旋转  
**根因**：pret/pokeemerald Brendan walking.png 原图9帧中：
- 帧2、帧5 是侧面帧，不属于 DOWN/UP 方向
- 当前映射 DOWN=[0,1,3]，但可能仍不完全正确

**下次接手第一件事**：用分格预览图重新逐帧确认正确帧索引，修改 `tools/convert_brendan_walk.py` 的 `SRC_FRAME_ORDER` 并重新运行

**相关文件**：
- `tools/convert_brendan_walk.py` → 修改 `SRC_FRAME_ORDER` 字典
- `assets/sprites/characters/player/calem_walk.png` → 重新生成后替换

原图9帧布局（初步分析）：
```
帧0: DOWN idle      帧1: DOWN walk步1   帧2: SIDE右侧
帧3: DOWN walk步2   帧4: UP idle        帧5: SIDE右侧走
帧6: LEFT idle      帧7: LEFT walk步1   帧8: LEFT walk步2
```

## 美术资源状态

- 宝可梦战斗精灵：✅ 静态PNG（16只）+ 动画精灵表（19只）
- 玩家行走精灵：✅ 已替换为 Brendan GBA 像素图（动画有 bug 待修）
- 地图图块集：❌ 未获取（推荐 The Spriters Resource，Pokemon X/Y Tilesets）
- 字体：❌ 未下载（需 PixelMplus12、m5x7、DotGothic16）
- UI 图集：❌ 未获取
