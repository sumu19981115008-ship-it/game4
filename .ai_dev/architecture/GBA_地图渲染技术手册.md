# GBA 地图渲染技术手册

> 适用于 pret/pokeemerald 反汇编资源 → Godot 4 PNG 背景图渲染流程

---

## 1. 数据来源

所有二进制数据从 pret/pokeemerald GitHub 仓库实时下载：

```
BASE_URL = https://raw.githubusercontent.com/pret/pokeemerald/master

地图 blockdata：data/layouts/{MapName}/map.bin
Primary metatile：data/tilesets/primary/{name}/metatiles.bin
Secondary metatile：data/tilesets/secondary/{name}/metatiles.bin
图块图像：assets/tilesets/{primary|secondary}/{name}/tiles.png（本地已缓存）
调色板：assets/tilesets/{primary|secondary}/{name}/palettes/{00-15}.pal（本地已缓存）
```

Littleroot Town 配置：
- Primary: `gTileset_General` → `primary_general`
- Secondary: `gTileset_Petalburg` → `secondary_petalburg`
- 布局来源：`data/layouts/layouts.json` → `LAYOUT_LITTLEROOT_TOWN`

---

## 2. 数据结构

### map.bin
- 格式：`MAP_W × MAP_H` 个 uint16，小端序
- `cell = uint16`
  - bits[9:0] = metatile_idx（0–1023）
  - bits[11:10] = collision（0=可走，1=实心，2/3少用）

### metatiles.bin
- 每个 metatile = 16 bytes = 8 × uint16
  - entries[0..3] = 底层（bottom layer），2×2 个 8px 图块
  - entries[4..7] = 顶层（top layer），2×2 个 8px 图块
- 每个 entry（uint16）：
  - bits[9:0] = tile_raw（全局 tile index）
  - bit[10] = hflip
  - bit[11] = vflip
  - bits[15:12] = pal_slot（0–15）

### tile_raw 寻址规则
```python
if tile_raw >= 512:
    arr = pet_raw        # secondary tileset 图块数组
    tidx = tile_raw - 512
else:
    arr = gen_raw        # primary tileset 图块数组
    tidx = tile_raw
```

**注意**：metatile 来自 secondary tileset 时，同样要用此规则——entry 里 tile_raw < 512 仍查 gen。

### 调色板 combined 构建规则
```python
# combined[N]（N = pal_slot，0–15）：
# N < 6  → gen_pals[N]
# N >= 6 → pet_pals[N - 6]
```

每个 slot 16 个颜色，combined 共 256 色。

### 透明规则
- `local_idx == 0`：透明（GBA 惯例，index 0 = 背景色）
- `(r,g,b) == (255,0,255)`：品红占位色，视同透明

---

## 3. 渲染流程

```python
for row in range(MAP_H):
    for col in range(MAP_W):
        meta_idx = cells[row*MAP_W+col] & 0x3FF
        combined = pick_combined(meta_idx)   # 见第4节

        # 渲染 metatile（16×16px）
        canvas = zeros(16, 16, 4)
        for layer in [bottom=0, top=1]:
            for sub in [0,1,2,3]:  # 2×2 排列
                entry = entries[layer*4+sub]
                tile_rgba = get_tile_rgba(...)
                if layer == 0:
                    canvas[py:py+8, px:px+8] = tile_rgba      # 底层直接写
                else:
                    mask = tile_rgba[:,:,3] > 0
                    canvas[py:py+8, px:px+8][mask] = tile_rgba[mask]  # 顶层只写非透明

        # 底层品红处理：is_bottom=True 时品红替换为相邻颜色（不透明）
        # 超出范围 tile：用 _safe_color(combined, pal_slot, 1) 纯色填充
```

---

## 4. 调色板 Override 规则（Littleroot Town）

不同建筑类型的 metatile 需要不同的 combined 来获得正确颜色：

```python
HOUSE_METAS = {520,521,522,528,529,530,536,537,538,
               544,545,546,547,552,553,554,555,
               560,561,562,568,569,570,576,584}
# override: slot10 → pet[1]（橙棕色屋顶瓦）

LAB_TOP_METAS = {524,525,526,578,579}
# override: slot8 → pet[9]（橙色横条纹，顶部装饰横梁）

LAB_BODY_METAS = {527,532,533,534,535,542,543,550,551,
                  556,557,564,565,577,585,586,587}
# override: slot8 → pet[3]（灰/砖红，玻璃幕墙+下部砖墙）
#           slot14 → pet[3]
```

其余 metatile 使用默认 combined（无 override）。

### 为什么需要 Override？

GBA 运行时通过硬件调色板寄存器动态切换颜色，同一张 tiles.png 配不同调色板显示不同颜色。反汇编的 tiles.png 只存了图块形状（索引图），颜色必须在运行时重新组合。

Override 的本质是：**为不同建筑类型人工指定某个 slot 应该引用哪个 .pal 文件**。

---

## 5b. 室内地图调色板规则（重要区别）

室内地图（primary_building + secondary_*）的 pal_slot 是**硬件绝对编号**，不是相对偏移：

```python
# 室内地图 combined[N] 构建规则（与室外不同！）
# N < 6  → bld_pals[N]    （primary building）
# N >= 6 → ctr_pals[N]    （secondary，绝对索引，不减 6！）

# 错误（套室外规则）：N>=6 → ctr_pals[N-6]  ← 会全黑
# 正确（室内规则）：  N>=6 → ctr_pals[N]
```

原因：secondary .pal 文件名 `06.pal` 对应硬件 slot 6，metatile entry 里 `pal_slot=6` 就要查 `06.pal`（即 `ctr_pals[6]`）。室外地图 secondary 从 slot 6 开始也正好对应 `pet_pals[0]`，但室内 secondary 的有效 .pal 从文件 06 开始，绝对编号一致。

---

## 5. 推广到其他城镇地图

### 步骤

1. 查找目标地图的 layout：
   ```
   GET https://raw.githubusercontent.com/pret/pokeemerald/master/data/layouts/layouts.json
   找到 id = LAYOUT_{MapName}，获取 primary_tileset, secondary_tileset, blockdata_filepath
   ```

2. 下载 map.bin、primary metatiles.bin、secondary metatiles.bin

3. 确认本地是否已有对应 tileset 目录（`assets/tilesets/`），没有则用 `tools/bake_tileset_palettes.py` 下载并烘焙

4. 分析各建筑的 metatile 集合（扫描 map.bin 里出现的 metatile idx 范围）

5. 用 `python3 tools/render_littleroot.py`（改参数后）渲染

### 已渲染地图 Override 汇总

| 地图 | Metatile 集合 | Override |
|------|--------------|---------|
| Littleroot Town | HOUSE_METAS（25个，gen）| slot10 → pet[1]（橙棕屋顶）|
| Littleroot Town | LAB_TOP_METAS（5个，gen）| slot8 → pet[9]，slot14 → pet[9] |
| Littleroot Town | LAB_BODY_METAS（18个，gen）| slot8,14 → pet[3] |
| Route 101 | 全部（31个，gen only）| 无 override（纯草地/路径）|
| Oldale Town | 620–639（pet，屋顶区）| slot9 → pet[9]，slot10 → pet[10] |
| Oldale Town | 640–655（pet，主体区）| slot9 → pet[9]，slot10 → pet[10] |

### 已下载的 Tileset 目录

```
assets/tilesets/
  primary_general/          ← 通用草地/路/水
  primary_building/         ← 室内建筑
  secondary_petalburg/      ← Littleroot/Route101 等
  secondary_cave/
  secondary_fortree/
  secondary_mauville/
  secondary_pokemon_center/
  secondary_rustboro/
  secondary_slateport/
  secondary_sootopolis/
```

### Override 分析方法

对新地图扫描各 metatile 的 pal_slot 分布：
```python
for mi in unique_meta_idxs:
    entries = struct.unpack_from('<8H', meta_raw, offset)
    slots = {(e>>12)&0xF for e in entries}
    print(f'meta[{mi}] slots={slots}')
```

然后对比各 pet_pals[N] 颜色值与参考截图，确定 override 映射。

---

## 6. 碰撞数据

碰撞从 `map.bin` 的 bits[11:10] 直接读取，导出到 `assets/maps/{name}.json`：

```json
{
  "collision": [[0,1,1,...], [0,0,1,...], ...]
}
```

Godot 场景（`LittlerootTown.gd`）读取 JSON，按行合并连续 solid 格创建 `StaticBody2D`：
- `collision_layer = 4`（WALL = bit2）
- 玩家 `collision_mask = 190`（包含 bit2，可碰 WALL）

---

## 7. 关键文件路径

| 文件 | 用途 |
|------|------|
| `tools/render_littleroot.py` | 渲染脚本（可复用，改参数后支持任意地图） |
| `tools/bake_tileset_palettes.py` | 将 .pal 烘焙进 tiles_rgba.png |
| `assets/maps/littleroot_town.png` | 渲染输出（320×320，Godot Sprite2D 背景） |
| `assets/maps/littleroot_town.json` | 碰撞/spawn/传送数据 |
| `scripts/world/zones/LittlerootTown.gd` | 加载 PNG + JSON，建碰撞体，定位玩家 |
| `scenes/world/zones/LittlerootTown.tscn` | 场景入口，Main.gd 启动时跳转 |
