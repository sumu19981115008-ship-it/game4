#!/usr/bin/env python3
"""
渲染 Littleroot Town 地图为 PNG。
用法：python3 tools/render_littleroot.py
输出：assets/maps/littleroot_town.png（320×320）
"""
import urllib.request
import struct
import numpy as np
from pathlib import Path
from PIL import Image

# ── 常量 ─────────────────────────────────────────────────────────────────────
GAME_ROOT = Path(__file__).parent.parent
GEN_DIR   = GAME_ROOT / 'assets/tilesets/primary_general'
PET_DIR   = GAME_ROOT / 'assets/tilesets/secondary_petalburg'
OUT_PATH  = GAME_ROOT / 'assets/maps/littleroot_town.png'

BASE_URL  = 'https://raw.githubusercontent.com/pret/pokeemerald/master'
MAP_W, MAP_H = 20, 20
TILE_PX = 8    # GBA 原始图块像素
META_PX = 16   # 输出 metatile 像素（2×TILE_PX）

# metatile 分组（决定用哪套调色板 override）
HOUSE_METAS = {
    520, 521, 522, 528, 529, 530, 536, 537, 538,
    544, 545, 546, 547, 552, 553, 554, 555,
    560, 561, 562, 568, 569, 570, 576, 584,
}
# 研究所顶行（橙色横条纹）：slot8 → pet[9]（暖橙）
LAB_TOP_METAS = {524, 525, 526, 578, 579}
# 研究所主体（灰色玻璃幕墙 + 砖红下部）：slot8 → pet[3]（灰/砖红）
LAB_BODY_METAS = {
    527, 532, 533, 534, 535,
    542, 543, 550, 551, 556, 557, 564, 565,
    577, 585, 586, 587,
}
LAB_METAS = LAB_TOP_METAS | LAB_BODY_METAS


# ── 工具函数 ──────────────────────────────────────────────────────────────────
def dl(url: str) -> bytes:
    return urllib.request.urlopen(url, timeout=15).read()


def parse_pal(path: Path) -> list:
    colors = []
    with open(path, 'r', errors='replace') as f:
        lines = [l.strip() for l in f.readlines()]
    for line in lines[3:]:
        parts = line.split()
        if len(parts) == 3:
            try:
                colors.append(tuple(int(x) for x in parts))
            except ValueError:
                pass
    return (colors + [(0, 0, 0)] * 16)[:16]


def load_pals(pal_dir: Path) -> list:
    pals = []
    for i in range(16):
        p = pal_dir / 'palettes' / f'{i:02d}.pal'
        pals.append(parse_pal(p) if p.exists() else [(0, 0, 0)] * 16)
    return pals


def make_combined(gen_pals, pet_pals, overrides: dict = None) -> list:
    """
    构建 256 色调色板。
    combined[N]: N<6 → gen_pals[N], N≥6 → pet_pals[N-6]
    overrides: {slot_N: pet_index} 将指定 slot 替换为 pet_pals[pet_index]
    """
    overrides = overrides or {}
    combined = []
    for N in range(16):
        if N in overrides:
            base_pal = pet_pals[overrides[N]]
        elif N < 6:
            base_pal = gen_pals[N]
        else:
            base_pal = pet_pals[N - 6]
        combined.extend(base_pal[:16])
    return combined  # 256 entries of (r,g,b)


def _safe_color(combined, pal_slot, local_idx):
    """查找颜色，遇到品红占位色则取同 slot 相邻索引的颜色替代。"""
    for delta in range(16):
        ci = pal_slot * 16 + ((local_idx + delta) % 16)
        if ci < len(combined):
            r, g, b = combined[ci]
            if not (r == 255 and g == 0 and b == 255):
                return r, g, b
    return 0, 0, 0


def get_tile_rgba(arr, cols_per_row, tile_idx, hflip, vflip, pal_slot, combined,
                  is_bottom=False):
    tx = (tile_idx % cols_per_row) * TILE_PX
    ty = (tile_idx // cols_per_row) * TILE_PX
    if ty + TILE_PX > arr.shape[0] or tx + TILE_PX > arr.shape[1]:
        # 超出范围的图块：用该 slot 的 index 1 做纯色填充
        r, g, b = _safe_color(combined, pal_slot, 1)
        return np.full((TILE_PX, TILE_PX, 4), [r, g, b, 255], dtype=np.uint8)

    block = arr[ty:ty + TILE_PX, tx:tx + TILE_PX]
    rgba = np.zeros((TILE_PX, TILE_PX, 4), dtype=np.uint8)
    for py in range(TILE_PX):
        for px in range(TILE_PX):
            li = int(block[py, px])
            local_idx = li % 16
            color_idx = pal_slot * 16 + local_idx
            if color_idx < len(combined):
                r, g, b = combined[color_idx]
            else:
                r, g, b = 0, 0, 0
            is_magenta = (r == 255 and g == 0 and b == 255)
            if local_idx == 0:
                alpha = 0
            elif is_magenta:
                if is_bottom:
                    # 底层：品红占位色用相邻颜色替代，保持不透明
                    r, g, b = _safe_color(combined, pal_slot, local_idx + 1)
                    alpha = 255
                else:
                    alpha = 0  # 顶层：品红透明
            else:
                alpha = 255
            rgba[py, px] = [r, g, b, alpha]

    if hflip:
        rgba = rgba[:, ::-1, :]
    if vflip:
        rgba = rgba[::-1, :, :]
    return rgba


def render_metatile(global_idx, gen_meta_raw, pet_meta_raw,
                    gen_arr, gen_cols, pet_arr, pet_cols, combined):
    is_pet = global_idx >= 512
    if is_pet:
        raw_data = pet_meta_raw
        off = (global_idx - 512) * 16
    else:
        raw_data = gen_meta_raw
        off = global_idx * 16

    entries = struct.unpack_from('<8H', raw_data, off)
    canvas = np.zeros((META_PX, META_PX, 4), dtype=np.uint8)

    for layer in range(2):
        for sub in range(4):
            entry = entries[layer * 4 + sub]
            tile_raw = entry & 0x3FF
            hflip    = bool(entry & 0x400)
            vflip    = bool(entry & 0x800)
            pal_slot = (entry >> 12) & 0xF

            px = (sub % 2) * TILE_PX
            py = (sub // 2) * TILE_PX

            # 决定从 gen 还是 pet 取图块
            is_bottom = (layer == 0)
            if tile_raw >= 512:
                tile_idx = tile_raw - 512
                tile_rgba = get_tile_rgba(pet_arr, pet_cols, tile_idx,
                                          hflip, vflip, pal_slot, combined,
                                          is_bottom=is_bottom)
            else:
                tile_rgba = get_tile_rgba(gen_arr, gen_cols, tile_raw,
                                          hflip, vflip, pal_slot, combined,
                                          is_bottom=is_bottom)

            if layer == 0:
                canvas[py:py + TILE_PX, px:px + TILE_PX] = tile_rgba
            else:
                mask = tile_rgba[:, :, 3] > 0
                for c in range(4):
                    canvas[py:py + TILE_PX, px:px + TILE_PX, c][mask] = tile_rgba[:, :, c][mask]

    return canvas


# ── 主流程 ────────────────────────────────────────────────────────────────────
def main():
    print('下载地图数据...')
    gen_meta_raw = dl(f'{BASE_URL}/data/tilesets/primary/general/metatiles.bin')
    pet_meta_raw = dl(f'{BASE_URL}/data/tilesets/secondary/petalburg/metatiles.bin')
    map_raw      = dl(f'{BASE_URL}/data/layouts/LittlerootTown/map.bin')

    print('加载图块图像和调色板...')
    gen_pals = load_pals(GEN_DIR)
    pet_pals = load_pals(PET_DIR)

    gen_img = Image.open(GEN_DIR / 'tiles.png')
    pet_img = Image.open(PET_DIR / 'tiles.png')
    gen_arr = np.array(gen_img)
    pet_arr = np.array(pet_img)
    gen_cols = gen_img.width // TILE_PX
    pet_cols = pet_img.width // TILE_PX

    # 构建各组的 combined 调色板
    # 默认（草地/路/水等）
    combined_def      = make_combined(gen_pals, pet_pals)
    # 房屋：slot10 → pet[1]（橙棕色屋顶）
    combined_house    = make_combined(gen_pals, pet_pals, {10: 1})
    # 研究所顶行：slot8 → pet[9]（橙色横条纹）, slot14 → pet[9]
    combined_lab_top  = make_combined(gen_pals, pet_pals, {8: 9, 14: 9})
    # 研究所主体：slot8 → pet[3]（灰/砖红）, slot14 → pet[3]
    combined_lab_body = make_combined(gen_pals, pet_pals, {8: 3, 14: 3})

    print('解析地图...')
    cells = struct.unpack_from(f'<{MAP_W * MAP_H}H', map_raw)

    print('渲染地图...')
    canvas = np.zeros((MAP_H * META_PX, MAP_W * META_PX, 3), dtype=np.uint8)

    for row in range(MAP_H):
        for col in range(MAP_W):
            meta_idx = cells[row * MAP_W + col] & 0x3FF

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
            py = row * META_PX
            px = col * META_PX
            # 将 RGBA 合并到 RGB（背景黑色）
            rgb  = tile[:, :, :3]
            alpha = tile[:, :, 3:4] / 255.0
            canvas[py:py + META_PX, px:px + META_PX] = (
                rgb * alpha + canvas[py:py + META_PX, px:px + META_PX] * (1 - alpha)
            ).astype(np.uint8)

    img = Image.fromarray(canvas, 'RGB')
    img.save(OUT_PATH)
    print(f'已保存：{OUT_PATH}（{img.size[0]}×{img.size[1]}px）')


if __name__ == '__main__':
    main()
