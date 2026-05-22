#!/usr/bin/env python3
"""
渲染草属性野外 RouteForest（40×30 metatile，640×480px）
漆黑魅影风格：
  - 高草丛密集分布路径两侧，不只是路边一格，而是大片区域
  - 蜿蜒主路，有两条分叉支路（一条死路探索、一条绕道）
  - 路径分叉处放告示牌/石头
  - 树木封闭边界，内部也有树木障碍组
  - 小水塘点缀（东北角）
  - 北侧出口 → StarterVillage；南侧出口 → NovaTown
用法：python3 tools/render_route_forest.py
输出：assets/maps/route_forest.png（640×480）
      assets/maps/route_forest.json
"""
import struct, json
import numpy as np
from pathlib import Path
from PIL import Image
from render_route101 import (
    dl, parse_pal, load_pals, make_combined,
    _safe_color, get_tile_rgba, render_metatile
)

GAME_ROOT = Path(__file__).parent.parent
GEN_DIR   = GAME_ROOT / 'assets/tilesets/primary_general'
PET_DIR   = GAME_ROOT / 'assets/tilesets/secondary_petalburg'
OUT_PNG   = GAME_ROOT / 'assets/maps/route_forest.png'
OUT_JSON  = GAME_ROOT / 'assets/maps/route_forest.json'

BASE_URL = 'https://raw.githubusercontent.com/pret/pokeemerald/master'
MAP_W, MAP_H = 40, 30
TILE_PX = 8
META_PX = 16

# ── metatile 常量 ──────────────────────────────────────────────────
G   = 1     # 普通草地
HG  = 485  # 高草丛（slot2 深绿纹理）（gen[5]，与 gen[6] 交替铺成大片）
HG2 = 487  # 高草丛变体
P   = 161  # 沙土路面（slot1 橙黄）
FL  = 4     # 花草

# 树木
TT  = 13    # 树顶左
TT2 = 14    # 树顶右
TB  = 21    # 树底左
TB2 = 22    # 树底右

# 岩石组（gen row2：64-95，棕色大石头）
ROCK_TL = 100; ROCK_TR = 101  # 岩石左上/右上
ROCK_BL = 116; ROCK_BR = 117  # 岩石左下/右下

# 水面（slot5 蓝色）
WAT = 289   # 水面中央（slot5）
WAT_TL = 280; WAT_TR = 281  # 水岸左边缘
WAT_BL = 296; WAT_BR = 297  # 水岸右边缘

# 告示牌
SIGN = 45

SOLID_METAS = (
    set(range(13, 32))   # 树木
    | set(range(64, 96)) # 岩石
    | {280, 281, 296, 297} # 水岸（不可走）
    | {289, 290, 292, 294, 295} # 水面
)

# 高草丛图案：2×2 tile 铺满
HG_PATCH = [
    [HG,  HG2, HG,  HG2],
    [HG2, HG,  HG2, HG ],
    [HG,  HG2, HG,  HG2],
    [HG2, HG,  HG2, HG ],
]

# 树木障碍块（4格宽 2格高）
TREE_BLOCK = [
    [TT,  TT,  TT,  TT ],
    [TT2, TT2, TT2, TT2],
]


def make_grid():
    W, H = MAP_W, MAP_H
    # 默认全部普通草地
    grid = [[G]*W for _ in range(H)]

    def fill(r, c, val):
        if 0 <= r < H and 0 <= c < W:
            grid[r][c] = val

    def hline(row, c0, c1, val=P):
        for c in range(max(0,c0), min(c1+1, W)):
            fill(row, c, val)

    def vline(col, r0, r1, val=P):
        for r in range(max(0,r0), min(r1+1, H)):
            fill(r, col, val)

    def rect(r0, c0, r1, c1, val):
        for r in range(max(0,r0), min(r1+1, H)):
            for c in range(max(0,c0), min(c1+1, W)):
                fill(r, c, val)

    def place(r0, c0, pattern):
        for dr, row_data in enumerate(pattern):
            for dc, val in enumerate(row_data):
                fill(r0+dr, c0+dc, val)

    # ── 四周树墙 ──────────────────────────────────────────────────
    for c in range(W):
        grid[0][c] = TT;  grid[1][c] = TT2
        grid[H-2][c] = TT; grid[H-1][c] = TT2
    for r in range(2, H-2):
        grid[r][0] = TT;   grid[r][1] = TT2
        grid[r][W-2] = TT; grid[r][W-1] = TT2

    # ── 北侧出口（col 10-11, row 0-1 打开）──────────────────────
    for r in [0, 1]:
        for c in [10, 11]:
            fill(r, c, P)

    # ── 南侧出口（col 18-19, row H-2, H-1 打开）─────────────────
    for r in [H-2, H-1]:
        for c in [18, 19]:
            fill(r, c, P)

    # ══════════════════════════════════════════════════════════════
    # 主路：蜿蜒从北出口到南出口
    # 北出口 col10-11 → 向南走直到 row6
    # row6 向右弯到 col18-19
    # col18-19 继续向南到南出口
    # ══════════════════════════════════════════════════════════════
    # 北段：竖向 col10-11, row0-6
    vline(10, 0, 6); vline(11, 0, 6)
    # 弯道横段：row6-7, col10-19
    hline(6, 10, 19); hline(7, 10, 19)
    # 南段：竖向 col18-19, row6-H-1
    vline(18, 6, H-1); vline(19, 6, H-1)

    # ══════════════════════════════════════════════════════════════
    # 分叉支路 A（死路，向东探索）：从 row14, col19 向右到 col30
    # ══════════════════════════════════════════════════════════════
    hline(14, 19, 30); hline(15, 19, 30)
    # 死路末端放岩石挡路
    place(13, 31, [[ROCK_TL, ROCK_TR], [ROCK_BL, ROCK_BR]])
    place(15, 31, [[ROCK_TL, ROCK_TR], [ROCK_BL, ROCK_BR]])

    # ══════════════════════════════════════════════════════════════
    # 分叉支路 B（绕道，向西）：从 row20, col10 向左到 col4，再向南到 row26
    # ══════════════════════════════════════════════════════════════
    hline(20, 4, 10); hline(21, 4, 10)
    vline(4, 21, 26); vline(5, 21, 26)
    # 绕道末端连回主路附近
    hline(26, 4, 19); hline(27, 4, 19)

    # ══════════════════════════════════════════════════════════════
    # 高草丛：大片覆盖路径两侧 3-4 格区域（漆黑魅影风格：密集）
    # ══════════════════════════════════════════════════════════════
    # 主路北段两侧（col 3-9 和 col 12-17，row 2-5）
    rect(2, 3, 5, 9,  HG)
    rect(2, 12, 5, 17, HG2)
    # 主路弯道下方两侧
    rect(8, 3,  13, 9,  HG)
    rect(8, 12, 13, 17, HG2)
    # 主路南段两侧（col 12-17 和 col 20-30，row 8-25）
    rect(8, 20, 13, 30, HG)
    rect(16, 20, 25, 35, HG2)
    # 绕道西侧草丛
    rect(22, 6, 25, 17, HG)
    # 东北角大片草丛（col 22-36, row 2-12）
    for r in range(2, 13):
        for c in range(22, 37):
            if grid[r][c] == G:
                grid[r][c] = HG if (r+c)%2==0 else HG2

    # ── 高草丛用交替格增加视觉多样性 ─────────────────────────────
    for r in range(2, H-2):
        for c in range(2, W-2):
            if grid[r][c] in [HG, HG2]:
                grid[r][c] = HG if (r+c)%2==0 else HG2

    # ══════════════════════════════════════════════════════════════
    # 内部树木障碍组（增加探索分支感）
    # ══════════════════════════════════════════════════════════════
    # 东南角树丛（col 30-35, row 18-23）
    for r in range(18, 24):
        for c in range(31, 36):
            fill(r, c, TT if r%2==0 else TT2)

    # 西侧中段树丛（col 2-3, row 10-16）已是边墙，额外加 col 6-7
    for r in range(10, 17):
        fill(r, 6, TT if r%2==0 else TT2)
        fill(r, 7, TT if r%2==0 else TT2)

    # ── 水塘（东北角 col 25-30, row 3-7）─────────────────────────
    # 水面
    rect(4, 26, 6, 29, WAT)
    # 水岸上边
    hline(3, 26, 29, WAT_TL)
    # 水岸下边
    hline(7, 26, 29, WAT_BL)
    # 岸边草地（把水塘周围的高草删掉变成普通草）
    rect(3, 25, 7, 30, G)
    rect(4, 26, 6, 29, WAT)
    fill(3, 26, WAT_TL); fill(3, 27, WAT_TL); fill(3, 28, WAT_TL); fill(3, 29, WAT_TR)
    fill(7, 26, WAT_BL); fill(7, 27, WAT_BL); fill(7, 28, WAT_BL); fill(7, 29, WAT_BR)

    # ── 告示牌（北路口 col 12, row 2）────────────────────────────
    fill(2, 12, SIGN)
    # 支路 A 路口告示牌
    fill(14, 20, SIGN)

    # ── 岩石点缀（主路弯道附近）──────────────────────────────────
    place(10, 13, [[ROCK_TL, ROCK_TR], [ROCK_BL, ROCK_BR]])

    # ── 散花装饰（草地上）────────────────────────────────────────
    flowers = [
        (3,3),(5,4),(9,4),(11,3),(13,8),(17,3),(19,4),(23,5),
        (9,21),(12,25),(14,32),(17,33),(22,22),(24,28),
        (26,8),(27,12),(28,15),
    ]
    for fr, fc in flowers:
        if 0<=fr<H and 0<=fc<W and grid[fr][fc] == G:
            grid[fr][fc] = FL

    return grid


def main():
    print('下载地图数据...')
    gen_meta_raw = dl(f'{BASE_URL}/data/tilesets/primary/general/metatiles.bin')
    pet_meta_raw = dl(f'{BASE_URL}/data/tilesets/secondary/petalburg/metatiles.bin')

    print('加载图块图像和调色板...')
    gen_pals = load_pals(GEN_DIR)
    pet_pals = load_pals(PET_DIR)

    gen_img = Image.open(GEN_DIR / 'tiles.png')
    pet_img = Image.open(PET_DIR / 'tiles.png')
    gen_arr = np.array(gen_img); gen_cols = gen_img.width // TILE_PX
    pet_arr = np.array(pet_img); pet_cols = pet_img.width // TILE_PX

    combined_def = make_combined(gen_pals, pet_pals)

    print('设计地图...')
    grid = make_grid()

    print('渲染地图...')
    canvas = np.zeros((MAP_H * META_PX, MAP_W * META_PX, 3), dtype=np.uint8)
    collision = []

    for row in range(MAP_H):
        coll_row = []
        for col in range(MAP_W):
            meta_idx = grid[row][col] & 0x3FF

            tile = render_metatile(
                meta_idx, gen_meta_raw, pet_meta_raw,
                gen_arr, gen_cols, pet_arr, pet_cols, combined_def
            )
            py = row * META_PX; px = col * META_PX
            rgb   = tile[:, :, :3]
            alpha = tile[:, :, 3:4] / 255.0
            canvas[py:py+META_PX, px:px+META_PX] = (
                rgb * alpha + canvas[py:py+META_PX, px:px+META_PX] * (1-alpha)
            ).astype(np.uint8)

            is_solid = meta_idx in SOLID_METAS
            coll_row.append(1 if is_solid else 0)
        collision.append(coll_row)

    img = Image.fromarray(canvas, 'RGB')
    img.save(OUT_PNG)
    print(f'已保存：{OUT_PNG}（{img.size[0]}×{img.size[1]}px）')

    map_json = {
        'width': MAP_W, 'height': MAP_H,
        'spawn': {'x': 10, 'y': 2},
        'collision': collision,
        'transitions': [
            {'x': 10, 'y': 0, 'target': 'res://scenes/world/zones/StarterVillage.tscn',
             'spawn_x': 10, 'spawn_y': 17},
            {'x': 11, 'y': 0, 'target': 'res://scenes/world/zones/StarterVillage.tscn',
             'spawn_x': 11, 'spawn_y': 17},
            {'x': 18, 'y': 29, 'target': 'res://scenes/world/zones/NovaTown.tscn',
             'spawn_x': 12, 'spawn_y': 1},
            {'x': 19, 'y': 29, 'target': 'res://scenes/world/zones/NovaTown.tscn',
             'spawn_x': 13, 'spawn_y': 1},
        ],
    }
    OUT_JSON.write_text(json.dumps(map_json, indent=2, ensure_ascii=False))
    print(f'已保存：{OUT_JSON}')


if __name__ == '__main__':
    main()
