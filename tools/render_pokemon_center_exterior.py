#!/usr/bin/env python3
"""
渲染宝可梦中心外观建筑（独立素材PNG）。
参考：口袋怪兽漆黑的魅影 GBA 风格，橙棕色圆顶+蓝色玻璃入口。
输出：
  assets/maps/buildings/pokemon_center_exterior.png  — 带透明背景的建筑本体
  assets/maps/buildings/pokemon_center_exterior.json — 碰撞+锚点数据
尺寸：3格宽 × 4格高（48×64px）

双 tileset 渲染：primary_general（metatile 定义 + tile 0-511）
                secondary_qihei（漆黑魅影专用，tile index >= 512 的部分从此读取）

metatile 来源：从漆黑魅影ROM提取，global index 893-919（secondary local 381-407）
  row0: 893, 894, 895  — 圆顶上层（橙棕色）
  row1: 901, 902, 903  — 圆顶中层
  row2: 909, 910, 911  — 墙体+玻璃
  row3: 917, 918, 919  — 入口层（蓝色玻璃门）
"""
import struct, json
import numpy as np
from pathlib import Path
from PIL import Image

GAME_ROOT  = Path(__file__).parent.parent
GEN_DIR    = GAME_ROOT / 'assets/tilesets/primary_general'
QH_DIR     = GAME_ROOT / 'assets/tilesets/secondary_qihei'
OUT_DIR    = GAME_ROOT / 'assets/maps/buildings'
OUT_PNG    = OUT_DIR / 'pokemon_center_exterior.png'
OUT_JSON   = OUT_DIR / 'pokemon_center_exterior.json'
CACHE_GEN  = Path(__file__).parent / '_gen_meta.bin'
CACHE_QH   = Path(__file__).parent / '_qihei_meta.bin'

TILE_PX  = 8
META_PX  = 16

# 漆黑魅影宝可梦中心外观布局（3格宽 × 4格高）
# 从漆黑魅影ROM地图直接提取的真实 metatile 编号（global index）
LAYOUT = [
    [893, 894, 895],  # 行0: 橙棕圆顶上层
    [901, 902, 903],  # 行1: 圆顶中层+侧面
    [909, 910, 911],  # 行2: 白色墙体
    [917, 918, 919],  # 行3: 蓝色玻璃入口
]

MAP_W = 3
MAP_H = 4

COLLISION = [
    [1, 1, 1],
    [1, 1, 1],
    [1, 1, 1],
    [1, 0, 1],  # 入口中央可通行
]


def parse_pal(path: Path) -> list:
    colors = []
    with open(path, 'r', errors='replace') as f:
        for line in f.readlines()[3:]:
            parts = line.split()
            if len(parts) == 3:
                try:
                    colors.append(tuple(int(x) for x in parts))
                except ValueError:
                    pass
    return (colors + [(0, 0, 0)] * 16)[:16]


def load_pals(pal_dir: Path) -> list:
    return [
        parse_pal(pal_dir / 'palettes' / f'{i:02d}.pal')
        if (pal_dir / 'palettes' / f'{i:02d}.pal').exists()
        else [(0, 0, 0)] * 16
        for i in range(16)
    ]


def make_combined(gen_pals, sec_pals) -> list:
    combined = []
    for N in range(16):
        base_pal = gen_pals[N] if N < 6 else sec_pals[N - 6]
        combined.extend(base_pal[:16])
    return combined


def get_tile_rgba(arr, cols, idx, hflip, vflip, ps, combined):
    tx = (idx % cols) * TILE_PX
    ty = (idx // cols) * TILE_PX
    if ty + TILE_PX > arr.shape[0] or tx + TILE_PX > arr.shape[1]:
        return np.zeros((TILE_PX, TILE_PX, 4), dtype=np.uint8)
    block = arr[ty:ty + TILE_PX, tx:tx + TILE_PX]
    rgba = np.zeros((TILE_PX, TILE_PX, 4), dtype=np.uint8)
    for py in range(TILE_PX):
        for px in range(TILE_PX):
            li = int(block[py, px]) % 16
            ci = ps * 16 + li
            r, g, b = combined[ci] if ci < len(combined) else (0, 0, 0)
            rgba[py, px] = [r, g, b, 0 if li == 0 else 255]
    if hflip:
        rgba = rgba[:, ::-1, :]
    if vflip:
        rgba = rgba[::-1, :, :]
    return rgba


def render_meta(meta_idx, gen_meta_raw, gen_arr, gen_cols,
                qh_meta_raw, qh_arr, qh_cols, combined):
    if meta_idx == 0:
        return np.zeros((META_PX, META_PX, 4), dtype=np.uint8)
    # global index >= 512 → secondary metatile
    if meta_idx >= 512:
        off = (meta_idx - 512) * 16
        raw = qh_meta_raw
    else:
        off = meta_idx * 16
        raw = gen_meta_raw
    if off + 16 > len(raw):
        return np.zeros((META_PX, META_PX, 4), dtype=np.uint8)
    entries = struct.unpack_from('<8H', raw, off)
    canvas = np.zeros((META_PX, META_PX, 4), dtype=np.uint8)
    for layer in range(2):
        for sub in range(4):
            e = entries[layer * 4 + sub]
            tile_raw = e & 0x3FF
            hflip = bool(e & 0x400)
            vflip = bool(e & 0x800)
            ps = (e >> 12) & 0xF
            px = (sub % 2) * TILE_PX
            py = (sub // 2) * TILE_PX
            if tile_raw >= 512:
                tile = get_tile_rgba(qh_arr, qh_cols, tile_raw - 512,
                                     hflip, vflip, ps, combined)
            else:
                tile = get_tile_rgba(gen_arr, gen_cols, tile_raw,
                                     hflip, vflip, ps, combined)
            if layer == 0:
                canvas[py:py + TILE_PX, px:px + TILE_PX] = tile
            else:
                mask = tile[:, :, 3] > 0
                for ch in range(4):
                    canvas[py:py + TILE_PX, px:px + TILE_PX, ch][mask] = tile[:, :, ch][mask]
    return canvas


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # 加载 metatiles.bin（优先使用本地缓存/提取的ROM数据）
    qh_meta_path = QH_DIR / 'metatiles.bin'
    if qh_meta_path.exists():
        print(f'使用漆黑魅影 secondary metatiles: {qh_meta_path}')
        qh_meta_raw = qh_meta_path.read_bytes()
    elif CACHE_QH.exists():
        qh_meta_raw = CACHE_QH.read_bytes()
    else:
        raise FileNotFoundError(
            f'找不到漆黑魅影 secondary metatiles，请先运行 ROM 提取脚本。\n'
            f'期望路径: {qh_meta_path}'
        )

    gen_meta_path = CACHE_GEN
    if gen_meta_path.exists():
        print(f'使用缓存 {gen_meta_path.name}')
        gen_meta_raw = gen_meta_path.read_bytes()
    else:
        import urllib.request
        print('下载 primary_general metatiles.bin...')
        gen_meta_raw = urllib.request.urlopen(
            'https://raw.githubusercontent.com/pret/pokeemerald/master'
            '/data/tilesets/primary/general/metatiles.bin', timeout=15
        ).read()
        gen_meta_path.write_bytes(gen_meta_raw)

    gen_pals = load_pals(GEN_DIR)
    qh_pals  = load_pals(QH_DIR)
    combined = make_combined(gen_pals, qh_pals)

    gen_img = Image.open(GEN_DIR / 'tiles.png')
    qh_img  = Image.open(QH_DIR / 'tiles.png')
    gen_arr = np.array(gen_img)
    qh_arr  = np.array(qh_img)
    gen_cols = gen_img.width // TILE_PX
    qh_cols  = qh_img.width // TILE_PX

    print(f'渲染宝可梦中心外观 {MAP_W}×{MAP_H} 格（{MAP_W*META_PX}×{MAP_H*META_PX}px）...')

    canvas = np.zeros((MAP_H * META_PX, MAP_W * META_PX, 4), dtype=np.uint8)

    for row, row_data in enumerate(LAYOUT):
        for col, meta_idx in enumerate(row_data):
            if meta_idx == 0:
                continue
            tile = render_meta(meta_idx, gen_meta_raw, gen_arr, gen_cols,
                               qh_meta_raw, qh_arr, qh_cols, combined)
            py = row * META_PX
            px = col * META_PX
            fg_a = tile[:, :, 3:4].astype(np.float32) / 255.0
            bg_a = canvas[py:py+META_PX, px:px+META_PX, 3:4].astype(np.float32) / 255.0
            out_a = fg_a + bg_a * (1 - fg_a)
            for ch in range(3):
                canvas[py:py+META_PX, px:px+META_PX, ch] = np.where(
                    out_a > 0,
                    (tile[:, :, ch:ch+1] * fg_a
                     + canvas[py:py+META_PX, px:px+META_PX, ch:ch+1] * bg_a * (1 - fg_a))
                    / np.where(out_a > 0, out_a, 1),
                    0
                ).squeeze().astype(np.uint8)
            canvas[py:py+META_PX, px:px+META_PX, 3] = (out_a * 255).squeeze().astype(np.uint8)

    # 贴精灵球 logo（GBA OBJ 层）：8×8，位于圆顶橙色平坦区中央 (x=20,y=14)
    pokeball = [
        [0, 0, 1, 1, 1, 1, 0, 0],
        [0, 1, 3, 3, 3, 3, 1, 0],
        [1, 3, 3, 3, 3, 3, 3, 1],
        [2, 2, 2, 1, 1, 2, 2, 2],
        [2, 2, 2, 1, 1, 2, 2, 2],
        [1, 2, 2, 2, 2, 2, 2, 1],
        [0, 1, 2, 2, 2, 2, 1, 0],
        [0, 0, 1, 1, 1, 1, 0, 0],
    ]
    col_map = {1: (60, 30, 10), 2: (255, 255, 255), 3: (200, 60, 40)}
    cx, cy = 20, 14
    for by, pb_row in enumerate(pokeball):
        for bx, v in enumerate(pb_row):
            if v == 0:
                continue
            xx, yy = cx + bx, cy + by
            if 0 <= xx < canvas.shape[1] and 0 <= yy < canvas.shape[0]:
                c = col_map[v]
                canvas[yy, xx] = [c[0], c[1], c[2], 255]

    img = Image.fromarray(canvas, 'RGBA')
    img_2x = img.resize((MAP_W * META_PX * 2, MAP_H * META_PX * 2), Image.NEAREST)
    img_2x.save(OUT_DIR / 'pokemon_center_exterior_2x.png')
    print(f'已保存2x预览：{OUT_DIR}/pokemon_center_exterior_2x.png')

    img.save(OUT_PNG)
    print(f'已保存：{OUT_PNG}（{img.width}×{img.height}px，RGBA透明背景）')

    data = {
        'width': MAP_W,
        'height': MAP_H,
        'tile_px': META_PX,
        'collision': COLLISION,
        'entrance': {'col': 1, 'row': 3},
        'interior_target': 'PokemonCenter_1F',
        'description': '宝可梦中心外观，漆黑魅影风格，橙棕圆顶+蓝色玻璃入口，3×4格',
    }
    OUT_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f'已保存：{OUT_JSON}')


if __name__ == '__main__':
    main()
