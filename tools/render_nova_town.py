#!/usr/bin/env python3
"""
渲染新城镇 NovaTown（30×28 metatile，480×448px）
布局：
  - 宝可梦中心（右侧 col=20, row=3），5×8
  - 宝可梦道馆（左中 col=3, row=8），6×6（Mauville 现代风格）
  - 普通民居 × 3（分散）
  - 告示牌广场（中央）+ 花圃装饰
  - 北门出口 → RouteForest
  - 东侧道路预留（未来扩展）
  - 道馆前广场石板路，中心喷泉（水面 metatile）
用法：python3 tools/render_nova_town.py
输出：assets/maps/nova_town.png（480×448）
      assets/maps/nova_town.json
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
OUT_PNG   = GAME_ROOT / 'assets/maps/nova_town.png'
OUT_JSON  = GAME_ROOT / 'assets/maps/nova_town.json'

BASE_URL = 'https://raw.githubusercontent.com/pret/pokeemerald/master'
MAP_W, MAP_H = 30, 28
TILE_PX = 8
META_PX = 16

# ── metatile 常量 ──────────────────────────────────────────────────
G   = 1    # 草地
P   = 161  # 沙土路面（slot1 橙黄）
FL  = 4    # 花草
W   = 289  # 水面（slot5 蓝色）

# 树木
TT  = 13; TT2 = 14; TB = 21; TB2 = 22

# 装饰
SIGN    = 45
MAILBOX = 488
ROCK_TL = 100; ROCK_TR = 101; ROCK_BL = 116; ROCK_BR = 117

# ── 宝可梦中心（gen primary，5×8）────────────────────────────────
PC = [
    [8,  9,  10,  9, 11],
    [16, 17,  18, 17, 18],
    [24, 25,  26, 25, 26],
    [40, 41,  42, 41, 43],
    [56, 57,  58, 57, 59],
    [72, 73,  74, 73, 75],
    [80, 81,  82, 81, 83],
    [88, 89,  90, 89, 91],
]

# ── 道馆（Mauville 风格，gen 426-461，6格宽 4格高）────────────────
# 从 custom_hub.py 的 GYM_MODERN 改写（已知 gen metatile）
GYM = [
    [426, 427, 427, 427, 427, 428],
    [434, 435, 435, 435, 435, 436],
    [440, 441, 442, 435, 443, 444],
    [P,   P,   450, 451, P,   P  ],
]

# ── 民居（petalburg secondary，5×4）──────────────────────────────
HOUSE_A = [
    [520, 521, 522, 521, 523],
    [528, 529, 530, 529, 531],
    [536, 537, 538, 537, 539],
    [544, 545, 546, 547, 548],
]

# 花圃（pet 576-591）
FLWR  = 576
HEDGE = 516

HOUSE_METAS    = {520, 521, 522, 523, 528, 529, 530, 531,
                  536, 537, 538, 539, 544, 545, 546, 547, 548}
LAB_TOP_METAS  = {524, 525, 526, 578, 579}
LAB_BODY_METAS = {527, 532, 533, 534, 535, 540, 541, 542, 543,
                  548, 549, 550, 551, 552, 553, 556, 557, 558, 559}
PC_METAS       = set(range(8, 92))
GYM_METAS      = set(range(426, 462))

SOLID_METAS = (
    set(range(13, 32))      # 树木
    | set(range(64, 96))    # 岩石
    | set(range(128, 160))  # 水面
    | PC_METAS | GYM_METAS
    | {HEDGE}
    | set(range(512, 570))  # pet 建筑主体
)


def make_grid():
    W, H = MAP_W, MAP_H
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

    # ── 北门出口（col 12-13, row 0-1 打开）──────────────────────
    for r in [0, 1]:
        for c in [12, 13]:
            fill(r, c, P)

    # ── 南门出口（col 12-13, row H-2, H-1 打开）──────────────────
    for r in [H-2, H-1]:
        for c in [12, 13]:
            fill(r, c, P)

    # ── 主路：南北纵向 col 12-13 贯通 ────────────────────────────
    vline(12, 0, H-1); vline(13, 0, H-1)

    # ── 横向主路：row 13-14，col 2-27 ────────────────────────────
    hline(13, 2, 27); hline(14, 2, 27)

    # ── 宝可梦中心（col 22, row 3），5×8 ─────────────────────────
    place(3, 22, PC)
    # PC 门前横路连接主路
    hline(11, 22, 26); hline(12, 22, 26)

    # ── 道馆（col 3, row 8），6×4 ─────────────────────────────────
    place(8, 3, GYM)
    # 道馆前广场（col 3-8, row 12-14 石板路）
    rect(12, 3, 14, 9, P)

    # ── 道馆前喷泉（水面 col 6, row 14-15）──────────────────────
    # 喷泉中心是2×2水面，周围石板
    fill(15, 6, W); fill(15, 7, W)
    fill(16, 6, W); fill(16, 7, W)
    rect(14, 5, 17, 8, P)
    fill(15, 6, W); fill(15, 7, W)
    fill(16, 6, W); fill(16, 7, W)

    # ── 民居 A（col 3, row 3），5×4 ──────────────────────────────
    place(3, 3, HOUSE_A)
    hline(7, 4, 6)

    # ── 民居 B（col 15, row 3），5×4 ─────────────────────────────
    place(3, 15, HOUSE_A)
    hline(7, 16, 18)
    # 连到主路
    vline(16, 7, 13)

    # ── 民居 C（col 20, row 16），5×4 ────────────────────────────
    place(16, 20, HOUSE_A)
    hline(20, 21, 23)
    vline(21, 20, 14)

    # ── 中央告示牌广场（col 10-14, row 15-17 花圃 + 告示牌）──────
    # 花圃围边
    hline(15, 10, 14, FLWR)
    hline(17, 10, 14, FLWR)
    vline(10, 15, 17, FLWR)
    vline(14, 15, 17, FLWR)
    # 广场中心石板
    rect(15, 11, 17, 13, P)
    # 中心告示牌
    fill(16, 12, SIGN)

    # ── PC 右侧花圃装饰 ──────────────────────────────────────────
    for c in range(22, 27):
        fill(11, c, FLWR)
    for c in range(22, 24):
        fill(2, c, FLWR)

    # ── 道馆右侧绿篱笆 ───────────────────────────────────────────
    vline(9, 7, 12, HEDGE)

    # ── 散花草地装饰 ─────────────────────────────────────────────
    flowers = [
        (3, 9),(4, 9),(5, 9),(6, 9),
        (3, 20),(4, 21),(5, 20),
        (18, 3),(19, 3),(20, 3),
        (18, 9),(19, 9),
        (21, 15),(22, 14),(23, 15),
        (18, 25),(19, 26),(20, 25),
        (23, 22),(24, 23),(25, 22),
    ]
    for fr, fc in flowers:
        if 0<=fr<H and 0<=fc<W and grid[fr][fc] == G:
            grid[fr][fc] = FL

    # ── 岩石（城镇东南装饰）─────────────────────────────────────
    place(22, 25, [[ROCK_TL, ROCK_TR], [ROCK_BL, ROCK_BR]])

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

    combined_def      = make_combined(gen_pals, pet_pals)
    combined_house    = make_combined(gen_pals, pet_pals, {10: 1})
    combined_lab_top  = make_combined(gen_pals, pet_pals, {8: 9, 14: 9})
    combined_lab_body = make_combined(gen_pals, pet_pals, {8: 3, 14: 3})

    print('设计地图...')
    grid = make_grid()

    print('渲染地图...')
    canvas = np.zeros((MAP_H * META_PX, MAP_W * META_PX, 3), dtype=np.uint8)
    collision = []

    for row in range(MAP_H):
        coll_row = []
        for col in range(MAP_W):
            meta_idx = grid[row][col] & 0x3FF

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
        'spawn': {'x': 12, 'y': 2},
        'collision': collision,
        'transitions': [
            {'x': 12, 'y': 0,   'target': 'res://scenes/world/zones/RouteForest.tscn',
             'spawn_x': 18, 'spawn_y': 27},
            {'x': 13, 'y': 0,   'target': 'res://scenes/world/zones/RouteForest.tscn',
             'spawn_x': 19, 'spawn_y': 27},
            {'x': 12, 'y': MAP_H-1, 'target': 'res://scenes/world/zones/RouteForest.tscn',
             'spawn_x': 18, 'spawn_y': 27},
            {'x': 13, 'y': MAP_H-1, 'target': 'res://scenes/world/zones/RouteForest.tscn',
             'spawn_x': 19, 'spawn_y': 27},
        ],
    }
    OUT_JSON.write_text(json.dumps(map_json, indent=2, ensure_ascii=False))
    print(f'已保存：{OUT_JSON}')


if __name__ == '__main__':
    main()
