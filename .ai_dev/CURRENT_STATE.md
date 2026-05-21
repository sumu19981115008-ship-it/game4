# 当前开发状态

**最后更新**：2026-05-21（Session 10）  
**当前阶段**：玩家行走动画帧修正完成，各方向帧已拆分至独立文件夹  
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
- [x] 玩家行走动画帧索引修正（SRC_FRAME_ORDER down=[0,1,2] up=[3,4,5] left=[6,7,8]）
- [x] 地图图块集下载（10场景 tiles.png + 调色板，assets/tilesets/）
- [x] TileMapZone.gd 替换 ProceduralMap，运行时创建 TileMap 并铺地图
- [x] Littleroot Town 完整还原（map.bin 解析 + metatile 双层渲染 + 调色板修复）
- [x] 民居/研究所分组渲染（HOUSE_METAS / LAB_TOP_METAS / LAB_BODY_METAS 精确集合）
- [x] 渲染脚本整理为可复用工具（tools/render_littleroot.py，支持任意地图扩展）
- [x] Route 101 渲染完成（tools/render_route101.py，320×320 PNG，含碰撞 JSON）
- [x] Oldale Town 渲染完成（tools/render_oldale.py，320×320 PNG，含碰撞 JSON）
- [x] Route101.gd / Route101.tscn 创建完成
- [x] OldaleTown.gd / OldaleTown.tscn 创建完成
- [x] metatile 扫描工具（tools/scan_metatile_slots.py，可复用于任意地图）
- [x] Petalburg City 渲染（30×30，480×480 PNG，含水路/建筑/道馆/宝可梦中心外观）
- [x] Pokemon Center 1F 室内渲染（14×9，224×144 PNG，橙色接待台/黄色地板）
- [x] PetalburgCity.gd / PetalburgCity.tscn 创建完成
- [x] PokemonCenter.gd / PokemonCenter.tscn 创建完成
- [x] 发现室内地图调色板规则：secondary pal_slot 是硬件绝对编号（N>=6 → ctr_pals[N] 不减6）
- [x] PlayerCamera.gd 重写：Camera2D limit 正确夹住地图边界 + 漆黑魅影风格黑色面板遮罩（CanvasLayer layer=10，四块 ColorRect 每帧跟随摄像机重新定位）
- [x] 所有 Zone .gd 更新为新签名 set_boundary(map_w_px, map_h_px)
- [x] 玩家行走动画帧重新映射（逐帧确认）：下/上/左/右 8个动画全部修正
- [x] 右方向 idle 帧通过 Python 将左侧 idle 水平翻转后写入精灵表第4列（r0c3）
- [x] 各方向帧拆分为独立 PNG 存入 上/下/左/右 文件夹，方便单独优化

## 待完成（下一步）

- [ ] **更多城镇/路线地图渲染**（Route102、Rustboro City 等）
- [ ] 战斗场景 UI
- [ ] HUD 视觉重做
- [ ] 战斗场景 UI（按 03_战斗系统策划案 布局）
- [ ] HUD 按 05_UI_UX策划案 重做视觉（深夜蓝配色、卢米奥金边框）
- [ ] 填充更多宝可梦 .tres 数据

## 已知问题

无

## 渲染技术状态

详见 `.ai_dev/architecture/GBA_地图渲染技术手册.md`

### 调色板 Override 映射（Littleroot Town）

| 组 | Metatile 集合 | Override |
|----|--------------|---------|
| 民居 | HOUSE_METAS（25个）| slot10 → pet[1]（橙棕屋顶）|
| 研究所顶行 | LAB_TOP_METAS（5个）| slot8 → pet[9]（橙色横条）|
| 研究所主体 | LAB_BODY_METAS（18个）| slot8,14 → pet[3]（灰/砖红）|
| 默认 | 其余所有 | 无 override |

### 渲染脚本

```bash
cd D:/fixelflow/game4
python3 tools/render_littleroot.py
# 输出：assets/maps/littleroot_town.png（320×320）
```

## 美术资源状态

- 宝可梦战斗精灵：✅ 静态PNG（16只）+ 动画精灵表（19只）
- 玩家行走精灵：✅ Calem/Brendan GBA 像素图，8方向动画全部修正，各帧独立存入 上/下/左/右 文件夹
- 地图图块集：✅ 10套 tileset（tiles.png + palettes）已下载
- 地图渲染：✅ Littleroot Town / Route 101 / Oldale Town（各 320×320）/ Petalburg City（480×480）/ Pokemon Center 1F（224×144）
- 字体：❌ 未下载（需 PixelMplus12、m5x7、DotGothic16）
- UI 图集：❌ 未获取
