# 开发交接文档

**最后更新**：2026-05-20（Session 5）  
**当前版本**：v0.1.0  
**接手时第一件事**：阅读本文档 → `ARCHITECTURE.md` → `.ai_dev/CURRENT_STATE.md`

---

## 项目现状一句话总结

底层架构 + 美术资源填充已完成，玩家可在程序化地图上行走并显示 Brendan 像素精灵。**存在一个高优先级 Bug：行走动画帧错位，下次开发第一件事就是修它。**

---

## 立即可运行

用 Godot 4.6 打开 `D:\fixelflow\game4\project.godot`，按 F5，工具栏点亮「输入」按钮，WASD 移动，Shift 奔跑。

---

## ✅ 已修复：行走动画旋转（2026-05-21）

**现象**：WASD 移动时人物像在旋转，走路夹杂侧身帧  
**根因**：`SRC_FRAME_ORDER` 中 down/up 帧索引错误（误以为帧2/5是侧面帧）  
**已修复**：逐帧目视确认后修正索引，重新生成精灵表

原图9帧实际布局（已目视确认）：
```
帧0: DOWN idle   帧1: DOWN walk步1   帧2: DOWN walk步2
帧3: UP   idle   帧4: UP   walk步1   帧5: UP   walk步2
帧6: LEFT idle   帧7: LEFT walk步1   帧8: LEFT walk步2
```

当前 `SRC_FRAME_ORDER`（正确值）：
```python
SRC_FRAME_ORDER = {
    "down":  [0, 1, 2],
    "up":    [3, 4, 5],
    "left":  [6, 7, 8],
}
```

---

## 当前资源状态

| 资源 | 状态 |
|------|------|
| 宝可梦静态精灵图 | ✅ 16只（front/back/shiny） |
| 战斗动画精灵表 | ✅ 19只 × 3变体（Showdown GIF 拆帧） |
| 玩家行走精灵 | ✅ Brendan GBA 像素图，帧索引已修正 |
| 宝可梦 .tres 数据 | ✅ 3只（妙蛙种子/小火龙/杰尼龟） |
| 技能 .tres 数据 | ✅ 5个（撞击/火焰喷射/水枪/藤鞭/催眠术） |
| DialogueBox / HUD | ✅ 已接入 TestZone |
| 地图图块集 | ❌ 未获取 |
| 字体 | ❌ 未下载 |
| UI 图集 | ❌ 未获取 |

---

## 代码关键文件速查

| 文件 | 作用 | 注意事项 |
|------|------|---------|
| `scripts/player/Player.gd` | 玩家移动+动画状态机 | `var anim: String =` 不能用 `:=`，Godot 4.6 无法推断类型 |
| `scripts/player/PlayerCamera.gd` | 相机跟随/边界 | zoom=2x，基准分辨率320×180 |
| `autoloads/PokemonDatabase.gd` | 宝可梦数据+精灵图接口 | get_sprite_texture() / get_anim_frames() |
| `scripts/world/ProceduralMap.gd` | 临时程序化地图 | 将来替换为TileMap时删除此文件 |
| `autoloads/EventBus.gd` | 全局信号总线 | 所有跨系统通信走这里 |
| `autoloads/SaveManager.gd` | 存档系统 | 方法名是 get_save_meta() 不是 get_meta() |
| `autoloads/AudioManager.gd` | 音频 | bgm_player/sfx_player 是普通变量，不是 @onready |
| `scripts/globals/CollisionLayers.gd` | 碰撞层常量 | extends Node（无 class_name，避免与 Autoload 名冲突） |
| `tools/convert_brendan_walk.py` | 玩家精灵生成工具 | 修改 SRC_FRAME_ORDER 后重新运行即可更新精灵表 |

---

## Godot 4.6 踩坑记录

1. **类型推断收紧**：`:=` 无法从 `Array/PackedStringArray` 等 Variant 子类推断，必须显式写类型（如 `var x: String = ...`）
2. **Autoload 与 class_name 不能同名**：脚本注册为 Autoload `Foo` 就不能再写 `class_name Foo`
3. **`_ready()` 中不能直接调用 `change_scene_to_file`**：必须用 `call_deferred`
4. **编辑器工具栏「输入」按钮**：每次 F5 运行后必须点亮，否则收不到键盘输入
5. **`@onready` 与动态 `add_child`**：`@onready` 在 `_ready()` 执行前赋值，动态创建的节点会拿到 null
6. **CanvasLayer 的显隐**：不是 CanvasItem，`hide()/show()` 无效，必须用 `visible = false/true`

---

## 美术资源来源参考

| 资源 | 来源 | URL规则 |
|------|------|---------|
| 宝可梦静态精灵 | PokeAPI / jsDelivr | `https://cdn.jsdelivr.net/gh/PokeAPI/sprites@master/sprites/pokemon/{id}.png` |
| 战斗动画 GIF | Pokémon Showdown | `https://play.pokemonshowdown.com/sprites/ani/{英文名}.gif`（需浏览器 UA） |
| 训练师行走图 | pret/pokeemerald | `https://raw.githubusercontent.com/pret/pokeemerald/master/graphics/object_events/pics/people/{人物}/walking.png` |
| 地图图块集 | The Spriters Resource | 搜索 `Pokemon X Y Tilesets`（16×16，免费同人用途） |

---

## 下一步开发优先级

1. **【美术】** 获取地图图块集，配置 TileSet 碰撞，替换 ProceduralMap
3. **【UI】** HUD 按 `docs/策划案/05_UI_UX策划案.md` 重做视觉（深夜蓝+卢米奥金）
4. **【功能】** 战斗场景 UI（按 `docs/策划案/03_战斗系统策划案.md` 布局）
5. **【数据】** 填充更多宝可梦 .tres（建议先做卡洛斯御三家 650/653/656）
