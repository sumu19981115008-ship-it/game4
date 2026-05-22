#!/usr/bin/env python3
"""
渲染 Petalburg City 地图为 PNG + JSON。
用法：python3 tools/render_petalburg.py
输出：assets/maps/petalburg_city.png（480×480）
      assets/maps/petalburg_city.json

Override 分析（scan 结果）：
  gen metatile 只用 slot 0/1/2/3/5，均为 gen_pals 范围内，无需 pet override
  pet metatile 513（slot 2,5）、572-614（slot 2/3）也无需特殊 override
  Petalburg 地图无高 slot（8/9/10）建筑 metatile，全部用默认 combined
"""
import urllib.request
import struct
import json
import numpy as np
from pathlib import Path
from PIL import Image

GAME_ROOT = Path(__file__).parent.parent
GEN_DIR   = GAME_ROOT / 'assets/tilesets/primary_general'
PET_DIR   = GAME_ROOT / 'assets/tilesets/secondary_petalburg'
OUT_PNG   = GAME_ROOT / 'assets/maps/petalburg_city.png'
OUT_JSON  = GAME_ROOT / 'assets/maps/petalburg_city.json'

BASE_URL  = 'https://raw.githubusercontent.com/pret/pokeemerald/master'
MAP_W, MAP_H = 30, 30
TILE_PX = 8
META_PX = 16


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
    return combined


def _safe_color(combined, pal_slot, local_idx):
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
                    r, g, b = _safe_color(combined, pal_slot, local_idx + 1)
                    alpha = 255
                else:
                    alpha = 0
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


def main():
    print('下载地图数据...')
    gen_meta_raw = dl(f'{BASE_URL}/data/tilesets/primary/general/metatiles.bin')
    pet_meta_raw = dl(f'{BASE_URL}/data/tilesets/secondary/petalburg/metatiles.bin')
    map_raw      = dl(f'{BASE_URL}/data/layouts/PetalburgCity/map.bin')

    print('加载图块图像和调色板...')
    gen_pals = load_pals(GEN_DIR)
    pet_pals = load_pals(PET_DIR)

    gen_img = Image.open(GEN_DIR / 'tiles.png')
    pet_img = Image.open(PET_DIR / 'tiles.png')
    gen_arr = np.array(gen_img)
    pet_arr = np.array(pet_img)
    gen_cols = gen_img.width // TILE_PX
    pet_cols = pet_img.width // TILE_PX

    # Petalburg 地图无高 slot 建筑，全部使用默认 combined
    combined_def = make_combined(gen_pals, pet_pals)

    print('解析地图...')
    cells = struct.unpack_from(f'<{MAP_W * MAP_H}H', map_raw)

    print('渲染地图...')
    canvas = np.zeros((MAP_H * META_PX, MAP_W * META_PX, 3), dtype=np.uint8)
    collision = []

    for row in range(MAP_H):
        coll_row = []
        for col in range(MAP_W):
            cell     = cells[row * MAP_W + col]
            meta_idx = cell & 0x3FF
            coll_val = (cell >> 10) & 0x3

            tile = render_metatile(
                meta_idx, gen_meta_raw, pet_meta_raw,
                gen_arr, gen_cols, pet_arr, pet_cols, combined_def
            )
            py = row * META_PX
            px = col * META_PX
            rgb   = tile[:, :, :3]
            alpha = tile[:, :, 3:4] / 255.0
            canvas[py:py + META_PX, px:px + META_PX] = (
                rgb * alpha + canvas[py:py + META_PX, px:px + META_PX] * (1 - alpha)
            ).astype(np.uint8)
            coll_row.append(1 if coll_val == 1 else 0)
        collision.append(coll_row)

    img = Image.fromarray(canvas, 'RGB')
    img.save(OUT_PNG)
    print(f'已保存：{OUT_PNG}（{img.size[0]}×{img.size[1]}px）')

    map_json = {
        'width': MAP_W,
        'height': MAP_H,
        'spawn': {'x': 15, 'y': 15},
        'collision': collision,
        'transitions': [],
    }
    OUT_JSON.write_text(json.dumps(map_json, indent=2, ensure_ascii=False))
    print(f'已保存：{OUT_JSON}')


if __name__ == '__main__':
    main()
