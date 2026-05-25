#!/usr/bin/env python3
"""
生成 metatile 预览图集（带编号标签），方便手工挑选建筑图块。
用法：python3 tools/preview_metatiles.py
输出：
  assets/maps/preview_building_metatiles.png   — primary_building 全部 metatile
  assets/maps/preview_pokemon_center_metatiles.png — secondary_pokemon_center 全部 metatile
"""
import urllib.request, struct
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

GAME_ROOT = Path(__file__).parent.parent
BLD_DIR   = GAME_ROOT / 'assets/tilesets/primary_building'
CTR_DIR   = GAME_ROOT / 'assets/tilesets/secondary_pokemon_center'
OUT_BLD   = GAME_ROOT / 'assets/maps/preview_building_metatiles.png'
OUT_CTR   = GAME_ROOT / 'assets/maps/preview_pokemon_center_metatiles.png'
CACHE_BLD = Path(__file__).parent / '_bld_meta.bin'
CACHE_CTR = Path(__file__).parent / '_ctr_meta.bin'

BASE_URL  = 'https://raw.githubusercontent.com/pret/pokeemerald/master'
TILE_PX   = 8
META_PX   = 16
COLS      = 16   # 每行几个 metatile

def dl(url):
    return urllib.request.urlopen(url, timeout=15).read()

def parse_pal(path):
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

def load_pals(pal_dir):
    return [parse_pal(pal_dir / 'palettes' / f'{i:02d}.pal')
            if (pal_dir / 'palettes' / f'{i:02d}.pal').exists()
            else [(0, 0, 0)] * 16
            for i in range(16)]

def make_combined_indoor(bld_pals, ctr_pals):
    combined = []
    for N in range(16):
        if N < 6:
            combined.extend(bld_pals[N][:16])
        else:
            combined.extend(ctr_pals[N][:16])
    return combined

def get_tile_rgba(arr, cols_per_row, tile_idx, hflip, vflip, pal_slot, combined, is_bottom=False):
    tx = (tile_idx % cols_per_row) * TILE_PX
    ty = (tile_idx // cols_per_row) * TILE_PX
    if ty + TILE_PX > arr.shape[0] or tx + TILE_PX > arr.shape[1]:
        return np.full((TILE_PX, TILE_PX, 4), [80, 80, 80, 255], dtype=np.uint8)
    block = arr[ty:ty + TILE_PX, tx:tx + TILE_PX]
    rgba = np.zeros((TILE_PX, TILE_PX, 4), dtype=np.uint8)
    for py in range(TILE_PX):
        for px in range(TILE_PX):
            li = int(block[py, px]) % 16
            ci = pal_slot * 16 + li
            r, g, b = combined[ci] if ci < len(combined) else (0, 0, 0)
            is_mag = (r == 255 and g == 0 and b == 255)
            if li == 0:
                alpha = 0
            elif is_mag:
                if is_bottom:
                    for d in range(1, 16):
                        ci2 = pal_slot * 16 + ((li + d) % 16)
                        if ci2 < len(combined):
                            rr, gg, bb = combined[ci2]
                            if not (rr == 255 and gg == 0 and bb == 255):
                                r, g, b = rr, gg, bb
                                break
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

def render_metatile(meta_idx, meta_raw, arr, cols, combined, is_secondary=False):
    local = meta_idx
    off = local * 16
    if off + 16 > len(meta_raw):
        return np.zeros((META_PX, META_PX, 4), dtype=np.uint8)
    entries = struct.unpack_from('<8H', meta_raw, off)
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
            tile = get_tile_rgba(arr, cols, tile_raw, hflip, vflip, pal_slot, combined, is_bottom)
            if layer == 0:
                canvas[py:py + TILE_PX, px:px + TILE_PX] = tile
            else:
                mask = tile[:, :, 3] > 0
                for ch in range(4):
                    canvas[py:py + TILE_PX, px:px + TILE_PX, ch][mask] = tile[:, :, ch][mask]
    return canvas

CELL_SIZE = META_PX * 3 + 14   # 放大3倍 + 编号文字区域

def make_preview(meta_raw, arr, cols_per_row, combined, label, out_path, is_secondary=False):
    total = len(meta_raw) // 16
    rows = (total + COLS - 1) // COLS
    W = COLS * CELL_SIZE
    H = rows * CELL_SIZE
    img = Image.new('RGB', (W, H), (30, 30, 30))
    draw = ImageDraw.Draw(img)

    for i in range(total):
        tile = render_metatile(i, meta_raw, arr, cols_per_row, combined, is_secondary)
        tile_img = Image.fromarray(
            np.where(tile[:, :, 3:4] > 0, tile[:, :, :3], np.full_like(tile[:, :, :3], 50)),
            'RGB'
        )
        tile_img = tile_img.resize((META_PX * 3, META_PX * 3), Image.NEAREST)

        col = i % COLS
        row = i // COLS
        x = col * CELL_SIZE + 1
        y = row * CELL_SIZE + 1
        img.paste(tile_img, (x, y))
        # 编号标签
        draw.text((x, y + META_PX * 3 + 1), f'{i}', fill=(200, 200, 100))

    img.save(out_path)
    print(f'已保存：{out_path}  ({total}个metatile，{W}×{H}px)')

def main():
    print('加载 primary_building tileset...')
    bld_pals = load_pals(BLD_DIR)
    ctr_pals = load_pals(CTR_DIR)
    bld_img  = Image.open(BLD_DIR / 'tiles.png')
    ctr_img  = Image.open(CTR_DIR / 'tiles.png')
    bld_arr  = np.array(bld_img)
    ctr_arr  = np.array(ctr_img)
    bld_cols = bld_img.width // TILE_PX
    ctr_cols = ctr_img.width // TILE_PX

    combined_bld = []
    for N in range(16):
        combined_bld.extend(bld_pals[N][:16])

    combined_ctr = make_combined_indoor(bld_pals, ctr_pals)

    def load_meta(cache, url_path):
        if cache.exists():
            print(f'  使用缓存：{cache.name}')
            return cache.read_bytes()
        print(f'  下载 {url_path}...')
        data = dl(f'{BASE_URL}/{url_path}')
        cache.write_bytes(data)
        return data

    bld_meta = load_meta(CACHE_BLD, 'data/tilesets/primary/building/metatiles.bin')
    ctr_meta = load_meta(CACHE_CTR, 'data/tilesets/secondary/pokemon_center/metatiles.bin')

    print(f'primary_building: {len(bld_meta)//16} 个metatile')
    print(f'secondary_pokemon_center: {len(ctr_meta)//16} 个metatile')

    print('生成 primary_building 预览...')
    make_preview(bld_meta, bld_arr, bld_cols, combined_bld,
                 'primary_building', OUT_BLD)

    print('生成 secondary_pokemon_center 预览...')
    make_preview(ctr_meta, ctr_arr, ctr_cols, combined_ctr,
                 'secondary_pokemon_center', OUT_CTR, is_secondary=True)

if __name__ == '__main__':
    main()
