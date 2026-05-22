#!/usr/bin/env python3
"""
渲染新手村 StarterVillage（22×20 metatile，352×320px）
布局：
  - 四周树木围边（2格宽）
  - 主角家：左侧（col=2, row=5），5×8 宽房屋
  - 博士研究所：中右（col=9, row=3），9×11 大楼（petalburg secondary）
  - 石板路：南北主路 + 南门出口
  - 花圃 / 信箱 / 告示牌 点缀
  - 南侧 row=19 中央出口 → 野外
用法：python3 tools/render_starter_village.py
输出：assets/maps/starter_village.png（352×320）
      assets/maps/starter_village.json
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
OUT_PNG   = GAME_ROOT / 'assets/maps/starter_village.png'
OUT_JSON  = GAME_ROOT / 'assets/maps/starter_village.json'

BASE_URL = 'https://raw.githubusercontent.com/pret/pokeemerald/master'
MAP_W, MAP_H = 22, 20
TILE_PX = 8
META_PX = 16

# ── metatile 常量 ──────────────────────────────────────────────────
G  = 1    # 草地
P  = 161  # 沙土路面（slot1 橙黄，Petalburg城镇路面）
FL = 4    # 花草
WAT = 297  # 水面（slot5 蓝色）

# 树木（gen）
TT  = 13   # 树顶左
TT2 = 14   # 树顶右
TB  = 21   # 树底左（灌木感）
TB2 = 22   # 树底右

# 信箱 gen[488]（棕色小方块）、告示牌 gen[45]（黄木牌）
MAILBOX = 45   # 告示牌/小标志（gen[45]）
SIGN    = 45   # 告示牌

# ── 民居：petalburg secondary，5格宽 × 4格高 ──────────────────────
# pet_meta 0-91 是 Petalburg 建筑图块
# 从 littleroot 已知的 HOUSE_METAS（520~584）：pet local 8-72
# pet 8-11   → 屋顶顶行（带烟囱）
# pet 16-19  → 屋顶下行（橙色）
# pet 24-27  → 墙体上（绿窗）
# pet 32-35  → 墙体下（门框）
# 宽5格用 [L, M, M, M, R] 模式
HOUSE_A = [
    [520, 521, 522, 521, 523],   # 屋顶顶
    [528, 529, 530, 529, 531],   # 屋顶下
    [536, 537, 538, 537, 539],   # 墙体上（窗）
    [544, 545, 546, 547, 548],   # 墙体下（门）
]

# ── 研究所：petalburg secondary 大楼，9格宽 × 9格高 ───────────────
# pet local 8-91（含侧翼屋檐）
# 顶行
LAB_T = [524, 525, 526, 525, 525, 525, 525, 526, 527]
# 中间主体（玻璃幕墙）
LAB_M = [532, 533, 534, 533, 533, 533, 533, 534, 535]
# 下体（砖红）
LAB_B = [540, 541, 542, 541, 541, 541, 541, 542, 543]
# 底部门廊
LAB_D = [548, 549, 550, 551, 551, 551, 550, 552, 553]
# 基座
LAB_F = [556, 557, 558, 557, 557, 557, 557, 558, 559]

LAB = [
    LAB_T,
    LAB_M, LAB_M,
    LAB_B, LAB_B,
    LAB_D,
    LAB_F,
]

# ── 花圃 pet[4] 绿篱笆 / pet[576]~[591] 花圃 ─────────────────────
HEDGE = 516   # pet local 4 = 516（绿篱笆）
FLWR  = 576   # pet local 64 = 576（花圃块）

SOLID_METAS = (
    set(range(13, 32))      # 树木
    | set(range(512, 560))  # pet 建筑主体
    | {HEDGE}
)

def make_grid():
    W, H = MAP_W, MAP_H
    grid = [[G]*W for _ in range(H)]

    def fill(r, c, val):
        if 0 <= r < H and 0 <= c < W:
            grid[r][c] = val

    def hline(row, c0, c1, val=P):
        for c in range(c0, min(c1+1, W)):
            fill(row, c, val)

    def vline(col, r0, r1, val=P):
        for r in range(r0, min(r1+1, H)):
            fill(r, col, val)

    def place(r0, c0, pattern):
        for dr, row_data in enumerate(pattern):
            for dc, val in enumerate(row_data):
                fill(r0+dr, c0+dc, val)

    # ── 四周树墙（2格宽）──────────────────────────────────────────
    for c in range(W):
        grid[0][c] = TT;  grid[1][c] = TT2
        grid[H-2][c] = TT; grid[H-1][c] = TT2
    for r in range(2, H-2):
        grid[r][0] = TT;  grid[r][1] = TT2
        grid[r][W-2] = TT; grid[r][W-1] = TT2

    # ── 南门出口（两格宽，row 18-19，col 10-11）──────────────────
    # 先把南墙树木打开
    for r in [H-2, H-1]:
        for c in [10, 11]:
            fill(r, c, P)

    # ── 石板路主路：纵向 col 10-11，从 row 12 到南门 ─────────────
    vline(10, 12, H-1)
    vline(11, 12, H-1)

    # ── 主角家（col 3, row 5），5×4 ───────────────────────────────
    place(5, 3, HOUSE_A)
    # 门前路径
    hline(9, 4, 6)

    # ── 研究所（col 9, row 2），9×7 ───────────────────────────────
    place(2, 9, LAB)
    # 研究所门前路径，连到主路
    hline(9, 9, 11)
    hline(10, 9, 11)
    hline(11, 9, 11)

    # ── 横向广场路（row 9~11，col 3-11）──────────────────────────
    for row in [9, 10, 11]:
        hline(row, 3, 11)

    # ── 花圃装饰（研究所左下角附近）─────────────────────────────
    for c in range(3, 6):
        fill(12, c, FLWR)
    for c in range(3, 6):
        fill(13, c, FLWR)

    # ── 信箱（主角家右边 col 8, row 9）───────────────────────────
    fill(9, 8, MAILBOX)

    # ── 告示牌（路口 col 9, row 12）──────────────────────────────
    fill(12, 9, SIGN)

    # ── 散花装饰（草地上随机花草）────────────────────────────────
    import random; random.seed(7)
    flower_positions = [
        (3,3),(3,7),(4,7),(14,3),(14,7),(15,5),
        (16,3),(16,7),(17,3),(17,5),(17,7),
        (3,14),(4,14),(5,14),(6,14),(7,14),
        (3,17),(5,17),(7,17),
    ]
    for fr, fc in flower_positions:
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

    # 调色板：民居用 override slot10→pet[1]（橙棕屋顶）
    # 研究所上部 slot8→pet[9]，下部 slot8→pet[3]
    combined_def      = make_combined(gen_pals, pet_pals)
    combined_house    = make_combined(gen_pals, pet_pals, {10: 1})
    combined_lab_top  = make_combined(gen_pals, pet_pals, {8: 9, 14: 9})
    combined_lab_body = make_combined(gen_pals, pet_pals, {8: 3, 14: 3})

    LAB_TOP_METAS  = {524, 525, 526, 578, 579}
    LAB_BODY_METAS = {527, 532, 533, 534, 535, 540, 541, 542, 543,
                      548, 549, 550, 551, 552, 553, 556, 557, 558, 559}
    HOUSE_METAS    = {520, 521, 522, 523, 528, 529, 530, 531,
                      536, 537, 538, 539, 544, 545, 546, 547, 548}

    print('设计地图...')
    grid = make_grid()

    print('渲染地图...')
    canvas = np.zeros((MAP_H * META_PX, MAP_W * META_PX, 3), dtype=np.uint8)
    collision = []

    for row in range(MAP_H):
        coll_row = []
        for col in range(MAP_W):
            mi = grid[row][col]
            meta_idx = mi & 0x3FF

            if meta_idx in HOUSE_METAS:
                combined = combined_house
            elif meta_idx in LAB_TOP_METAS:
                combined = combined_lab_top
            elif meta_idx in LAB_BODY_METAS:
                combined = combined_lab_body
            else:
                combined = combined_def

            tile = render_metatile(
                meta_idx, gen_meta_raw, pet_meta_raw,
                gen_arr, gen_cols, pet_arr, pet_cols, combined
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
        'spawn': {'x': 10, 'y': 16},
        'collision': collision,
        'transitions': [
            {'x': 10, 'y': 19, 'target': 'res://scenes/world/zones/RouteForest.tscn',
             'spawn_x': 10, 'spawn_y': 1},
            {'x': 11, 'y': 19, 'target': 'res://scenes/world/zones/RouteForest.tscn',
             'spawn_x': 11, 'spawn_y': 1},
        ],
    }
    OUT_JSON.write_text(json.dumps(map_json, indent=2, ensure_ascii=False))
    print(f'已保存：{OUT_JSON}')


if __name__ == '__main__':
    main()
