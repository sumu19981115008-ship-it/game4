#!/usr/bin/env python3
"""
渲染自定义大地图 CustomHub：60×50格，含宝可梦中心 + 18属性道馆
使用多个城市 secondary tileset，让各道馆外观各异：
  - 石头市（Rustboro）：石头/黄沙大楼风格
  - 枯叶市（Mauville）：现代蓝白道馆风格
  - 基石镇（primary_general）：经典 GYM 招牌风格
输出: assets/maps/custom_hub.png (960×800px)
      assets/maps/custom_hub.json
"""
import urllib.request, struct, json
import numpy as np
from pathlib import Path
from PIL import Image

GAME_ROOT = Path(__file__).parent.parent
GEN_DIR   = GAME_ROOT / 'assets/tilesets/primary_general'
RUS_DIR   = GAME_ROOT / 'assets/tilesets/secondary_rustboro'
MAU_DIR   = GAME_ROOT / 'assets/tilesets/secondary_mauville'
OUT_PNG   = GAME_ROOT / 'assets/maps/custom_hub.png'
OUT_JSON  = GAME_ROOT / 'assets/maps/custom_hub.json'
CACHE_GEN = Path(__file__).parent / '_gen_meta.bin'
CACHE_RUS = Path(__file__).parent / '_rustboro_meta.bin'
CACHE_MAU = Path(__file__).parent / '_mauville_meta.bin'

BASE_URL  = 'https://raw.githubusercontent.com/pret/pokeemerald/master'
MAP_W, MAP_H = 60, 50
TILE_PX = 8
META_PX = 16

# ═══════════════════════════════════════════════════════════════════
# Metatile 常量
# ═══════════════════════════════════════════════════════════════════

# 地面（primary_general）
G   = 1    # 草地
P   = 49   # 石板路
FL  = 4    # 花草装饰

# 树木（primary_general）
TREE_T  = 13   # 树顶左
TREE_T2 = 14   # 树顶右
TREE_B  = 29   # 树底左
TREE_B2 = 30   # 树底右

# ── 宝可梦中心 (primary_general, metatile 8-91) ──────────────────
# 5格宽 × 8格高，带标志性红色圆顶 + 精灵球图案
PC = [
    [8,  9,  10,  9, 11],   # 顶部红砖横梁
    [16, 17,  18, 17, 18],  # 红格纹墙上
    [24, 25,  26, 25, 26],  # 红格纹墙下
    [40, 41,  42, 41, 43],  # 蓝色弧形顶
    [56, 57,  58, 57, 59],  # 大红圆顶上
    [72, 73,  74, 73, 75],  # 大红圆顶下
    [80, 81,  82, 81, 83],  # 彩虹弧底
    [88, 89,  90, 89, 91],  # 入口门廊
]

# ── 风格A：经典GYM道馆 (primary_general, metatile 448-461) ──────
# 4格宽 × 4格高，GYM招牌+大门
GYM_CLASSIC = [
    [448, 449, 450, 451],   # GYM招牌层
    [304, 305, 306, 307],   # 门框层
    [304, 305, 306, 307],   # 建筑主体
    [P,   P,   P,   P  ],   # 门口路径
]

# ── 风格B：Mauville 现代蓝白道馆 (primary_general metatile 434-461) ─
# 6格宽 × 4格高，现代感蓝色玻璃大楼
GYM_MODERN = [
    [426, 427, 427, 427, 427, 428],  # 顶部横梁
    [434, 435, 435, 435, 435, 436],  # 主体上层
    [440, 441, 442, 435, 443, 444],  # 主体中层（带装饰）
    [P,   449, 450, 453, 451, P  ],  # 底部+大门
]

# ── 风格C：Rustboro 石头学院（secondary_rustboro, local 136-220）──
# 注意：TILESET_ID = 'rustboro'，metatile 编号需加 512
# 10格宽 × 6格高的大型石砌建筑
R = 512  # rustboro secondary offset
GYM_STONE = [
    [R+136, R+137, R+137, R+139, R+140, R+140, R+141, R+137, R+137, R+138],
    [R+283, R+144, R+145, R+147, R+148, R+148, R+149, R+145, R+145, R+146],
    [R+280, R+152, R+153, R+142, R+143, R+150, R+151, R+154, R+154, R+155],
    [R+280, R+160, R+161, R+156, R+157, R+157, R+158, R+162, R+162, R+163],
    [R+280, R+168, R+169, R+164, R+165, R+165, R+166, R+170, R+170, R+171],
    [P,     P,     P,     P,     P,     P,     P,     P,     P,     P    ],
]

SOLID = 0x400

# ═══════════════════════════════════════════════════════════════════
# 地图网格设计
# ═══════════════════════════════════════════════════════════════════

def make_grid():
    W, H = MAP_W, MAP_H
    grid = [[G] * W for _ in range(H)]

    def fill_path_h(row, c0, c1):
        for c in range(c0, min(c1, W)):
            grid[row][c] = P

    def fill_path_v(col, r0, r1):
        for r in range(r0, min(r1, H)):
            grid[r][col] = P

    def place(r0, c0, pattern):
        for dr, row_data in enumerate(pattern):
            for dc, val in enumerate(row_data):
                r, c = r0+dr, c0+dc
                if 0 <= r < H and 0 <= c < W:
                    grid[r][c] = val

    # ── 四周树墙（2格高）────────────────────────────────────────────
    for c in range(W):
        grid[0][c] = TREE_T;   grid[1][c] = TREE_T2
        grid[H-2][c] = TREE_T; grid[H-1][c] = TREE_T2
    for r in range(2, H-2):
        grid[r][0] = TREE_B;   grid[r][1] = TREE_B2
        grid[r][W-2] = TREE_B; grid[r][W-1] = TREE_B2

    # ── 主干路 ────────────────────────────────────────────────────
    fill_path_h(24, 2, W-2)
    fill_path_h(25, 2, W-2)
    fill_path_v(29, 2, H-2)
    fill_path_v(30, 2, H-2)

    # ── 宝可梦中心（左上，col=3, row=3）─────────────────────────
    place(3, 3, PC)
    for c in range(3, 3+len(PC[0])):
        if 0 <= 3+len(PC) < H: grid[3+len(PC)][c] = P

    # ── 18个道馆，3种风格各6个，按属性分区 ───────────────────────
    # 布局：上半（row=3-22）左右各3列，下半（row=27-45）左右各3列
    # 纵向主路 col=29-30，横向主路 row=24-25
    # 风格A（经典GYM，4格宽）：上半左侧
    # 风格B（现代蓝白，6格宽）：上半右侧
    # 风格C（石头学院，10格宽）：下半，跨中心线

    # 风格A：经典小道馆，6个，上半左区
    gym_a_positions = [
        (3, 3+len(PC[0])+2),   # 宝可梦中心右边
        (3, 18),
        (12, 3), (12, 10), (12, 17), (12, 22),
    ]
    for r, c in gym_a_positions:
        place(r, c, GYM_CLASSIC)

    # 风格B：现代蓝白，6个，上半右区
    gym_b_positions = [
        (3, 33), (3, 41),
        (12, 33), (12, 41),
        (3, 49), (12, 49),
    ]
    for r, c in gym_b_positions:
        place(r, c, GYM_MODERN)

    # 风格C：石头学院，6个，下半（宽10格）
    gym_c_positions = [
        (27, 2), (27, 33),
        (36, 2), (36, 33),
        (42, 14), (42, 40),
    ]
    for r, c in gym_c_positions:
        place(r, c, GYM_STONE)

    # ── 散花装饰 ──────────────────────────────────────────────────
    import random; random.seed(42)
    for r in range(2, H-2):
        for c in range(2, W-2):
            if grid[r][c] == G and random.random() < 0.06:
                if all(
                    grid[r+dr][c+dc] == G
                    for dr,dc in [(-1,0),(1,0),(0,-1),(0,1)]
                    if 0<=r+dr<H and 0<=c+dc<W
                ):
                    grid[r][c] = FL

    return grid


# ═══════════════════════════════════════════════════════════════════
# 渲染核心
# ═══════════════════════════════════════════════════════════════════

def dl(url):
    return urllib.request.urlopen(url, timeout=15).read()

def parse_pal(path):
    colors = []
    with open(path, 'r', errors='replace') as f:
        for line in f.readlines()[3:]:
            parts = line.split()
            if len(parts) == 3:
                try: colors.append(tuple(int(x) for x in parts))
                except: pass
    return (colors + [(0,0,0)]*16)[:16]

def load_pals(pal_dir):
    return [parse_pal(pal_dir/'palettes'/f'{i:02d}.pal') if (pal_dir/'palettes'/f'{i:02d}.pal').exists()
            else [(0,0,0)]*16 for i in range(16)]

def make_combined(gen_pals, sec_pals):
    combined = []
    for n in range(16):
        combined.extend(gen_pals[n][:16] if n < 6 else sec_pals[n-6][:16])
    return combined

def _safe_color(combined, ps, li):
    for d in range(16):
        ci = ps*16 + ((li+d) % 16)
        if ci < len(combined):
            r,g,b = combined[ci]
            if not (r==255 and g==0 and b==255): return r,g,b
    return 0,0,0

def get_tile_rgba(arr, cols, idx, hflip, vflip, ps, combined, is_bottom=False):
    tx = (idx%cols)*TILE_PX; ty = (idx//cols)*TILE_PX
    if ty+TILE_PX>arr.shape[0] or tx+TILE_PX>arr.shape[1]:
        return np.full((TILE_PX,TILE_PX,4),[30,30,30,255],dtype=np.uint8)
    block = arr[ty:ty+TILE_PX, tx:tx+TILE_PX]
    rgba = np.zeros((TILE_PX,TILE_PX,4),dtype=np.uint8)
    for py in range(TILE_PX):
        for px in range(TILE_PX):
            li = int(block[py,px]) % 16
            ci = ps*16 + li
            r,g,b = combined[ci] if ci < len(combined) else (0,0,0)
            is_mag = (r==255 and g==0 and b==255)
            if li == 0:
                alpha = 0
            elif is_mag:
                if is_bottom: r,g,b = _safe_color(combined,ps,li+1); alpha=255
                else: alpha=0
            else:
                alpha = 255
            rgba[py,px] = [r,g,b,alpha]
    if hflip: rgba = rgba[:,::-1,:]
    if vflip: rgba = rgba[::-1,:,:]
    return rgba

def render_metatile(global_idx,
                    gen_meta, gen_arr, gen_cols,
                    rus_meta, rus_arr, rus_cols,
                    mau_meta, mau_arr, mau_cols,
                    combined_gen, combined_rus, combined_mau):
    # 选 tileset
    if global_idx >= 1024:
        # mauville secondary: 用 mau offset
        # 我们没用到，保留给扩展
        return np.zeros((META_PX,META_PX,4),dtype=np.uint8)
    elif global_idx >= 512:
        # rustboro secondary
        local = global_idx - 512
        meta_raw = rus_meta; combined = combined_rus
        sec_arr = rus_arr; sec_cols = rus_cols
    else:
        local = global_idx
        meta_raw = gen_meta; combined = combined_gen
        sec_arr = None; sec_cols = 0

    off = local * 16
    if off + 16 > len(meta_raw):
        return np.zeros((META_PX,META_PX,4),dtype=np.uint8)

    entries = struct.unpack_from('<8H', meta_raw, off)
    canvas = np.zeros((META_PX,META_PX,4),dtype=np.uint8)

    for layer in range(2):
        for sub in range(4):
            entry = entries[layer*4+sub]
            tile_raw = entry & 0x3FF
            hflip    = bool(entry & 0x400)
            vflip    = bool(entry & 0x800)
            pal_slot = (entry >> 12) & 0xF
            px = (sub%2)*TILE_PX; py = (sub//2)*TILE_PX

            if tile_raw >= 512 and sec_arr is not None:
                arr = sec_arr; cols = sec_cols; idx = tile_raw-512
            else:
                arr = gen_arr; cols = gen_cols; idx = tile_raw

            is_bottom = (layer == 0)
            tile = get_tile_rgba(arr, cols, idx, hflip, vflip, pal_slot, combined, is_bottom)

            if layer == 0:
                canvas[py:py+TILE_PX, px:px+TILE_PX] = tile
            else:
                mask = tile[:,:,3] > 0
                for ch in range(4):
                    canvas[py:py+TILE_PX, px:px+TILE_PX, ch][mask] = tile[:,:,ch][mask]
    return canvas


# 需要判为 solid 的 metatile 集合
TREE_METAS = {TREE_T, TREE_T2, TREE_B, TREE_B2, 13, 14, 21, 22, 29, 30}
GEN_BLDG   = set(range(8,12)) | set(range(16,28)) | set(range(40,44)) | \
             set(range(56,60)) | set(range(72,76)) | set(range(80,84)) | \
             set(range(88,92)) | set(range(304,312)) | set(range(426,462))
RUS_BLDG   = set(range(512+136, 512+284))   # rustboro 建筑体
SOLID_SET  = TREE_METAS | GEN_BLDG | RUS_BLDG


def main():
    print('加载图块图像和调色板...')
    gen_pals = load_pals(GEN_DIR)
    rus_pals = load_pals(RUS_DIR)
    mau_pals = load_pals(MAU_DIR)

    gen_img = Image.open(GEN_DIR/'tiles.png')
    rus_img = Image.open(RUS_DIR/'tiles.png')
    mau_img = Image.open(MAU_DIR/'tiles.png')
    gen_arr = np.array(gen_img); gen_cols = gen_img.width//TILE_PX
    rus_arr = np.array(rus_img); rus_cols = rus_img.width//TILE_PX
    mau_arr = np.array(mau_img); mau_cols = mau_img.width//TILE_PX

    combined_gen = make_combined(gen_pals, gen_pals)   # gen only（slot6-15全用gen）
    combined_rus = make_combined(gen_pals, rus_pals)
    combined_mau = make_combined(gen_pals, mau_pals)

    print('加载 metatiles.bin...')
    def load_meta(cache, url_path):
        if cache.exists(): return cache.read_bytes()
        data = dl(f'{BASE_URL}/{url_path}')
        cache.write_bytes(data); return data

    gen_meta = load_meta(CACHE_GEN, 'data/tilesets/primary/general/metatiles.bin')
    rus_meta = load_meta(CACHE_RUS, 'data/tilesets/secondary/rustboro/metatiles.bin')
    mau_meta = load_meta(CACHE_MAU, 'data/tilesets/secondary/mauville/metatiles.bin')
    print(f'  gen={len(gen_meta)//16}, rus={len(rus_meta)//16}, mau={len(mau_meta)//16}')

    print('设计地图网格...')
    grid = make_grid()

    print(f'渲染 {MAP_W}×{MAP_H} 地图...')
    canvas    = np.zeros((MAP_H*META_PX, MAP_W*META_PX, 3), dtype=np.uint8)
    collision = []

    for row in range(MAP_H):
        coll_row = []
        for col in range(MAP_W):
            cell     = grid[row][col]
            meta_idx = cell & 0x3FF
            coll_val = (cell >> 10) & 0x3

            tile = render_metatile(
                meta_idx,
                gen_meta, gen_arr, gen_cols,
                rus_meta, rus_arr, rus_cols,
                mau_meta, mau_arr, mau_cols,
                combined_gen, combined_rus, combined_mau,
            )
            py = row*META_PX; px = col*META_PX
            rgb   = tile[:,:,:3]
            alpha = tile[:,:,3:4] / 255.0
            canvas[py:py+META_PX, px:px+META_PX] = (
                rgb * alpha + canvas[py:py+META_PX, px:px+META_PX] * (1-alpha)
            ).astype(np.uint8)

            is_solid = (coll_val==1) or (meta_idx in SOLID_SET)
            coll_row.append(1 if is_solid else 0)
        collision.append(coll_row)

    img = Image.fromarray(canvas, 'RGB')
    img.save(OUT_PNG)
    print(f'已保存: {OUT_PNG} ({img.size[0]}×{img.size[1]}px)')

    OUT_JSON.write_text(json.dumps({
        'width': MAP_W, 'height': MAP_H,
        'spawn': {'x': 29, 'y': 24},
        'collision': collision,
        'transitions': [],
    }, indent=2, ensure_ascii=False))
    print(f'已保存: {OUT_JSON}')


if __name__ == '__main__':
    main()
