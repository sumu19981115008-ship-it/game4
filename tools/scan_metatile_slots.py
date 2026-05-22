#!/usr/bin/env python3
"""
扫描指定地图 map.bin 里各 metatile 的 pal_slot 分布。
用法：python3 tools/scan_metatile_slots.py Route101
"""
import sys
import struct
import urllib.request
from pathlib import Path
from collections import defaultdict

GAME_ROOT = Path(__file__).parent.parent
BASE_URL  = 'https://raw.githubusercontent.com/pret/pokeemerald/master'

MAP_CONFIGS = {
    'Route101': {
        'map_bin':    'data/layouts/Route101/map.bin',
        'gen_meta':   'data/tilesets/primary/general/metatiles.bin',
        'pet_meta':   'data/tilesets/secondary/petalburg/metatiles.bin',
        'w': 20, 'h': 20,
    },
    'OldaleTown': {
        'map_bin':    'data/layouts/OldaleTown/map.bin',
        'gen_meta':   'data/tilesets/primary/general/metatiles.bin',
        'pet_meta':   'data/tilesets/secondary/petalburg/metatiles.bin',
        'w': 20, 'h': 20,
    },
}

def dl(url):
    return urllib.request.urlopen(url, timeout=15).read()

def main():
    name = sys.argv[1] if len(sys.argv) > 1 else 'Route101'
    cfg  = MAP_CONFIGS[name]

    print(f'下载 {name} 数据...')
    map_raw      = dl(f'{BASE_URL}/{cfg["map_bin"]}')
    gen_meta_raw = dl(f'{BASE_URL}/{cfg["gen_meta"]}')
    pet_meta_raw = dl(f'{BASE_URL}/{cfg["pet_meta"]}')

    cells   = struct.unpack_from(f'<{cfg["w"]*cfg["h"]}H', map_raw)
    used_mi = sorted({c & 0x3FF for c in cells})

    print(f'\n{name} 地图使用的 metatile 共 {len(used_mi)} 个：')
    print(f'范围：{min(used_mi)}–{max(used_mi)}\n')

    # 按 pal_slot 集合分组
    slot_groups = defaultdict(list)
    for mi in used_mi:
        is_pet = mi >= 512
        raw    = pet_meta_raw if is_pet else gen_meta_raw
        off    = (mi - 512 if is_pet else mi) * 16
        if off + 16 > len(raw):
            continue
        entries  = struct.unpack_from('<8H', raw, off)
        slots    = frozenset((e >> 12) & 0xF for e in entries)
        slot_groups[slots].append(mi)

    print('按 pal_slot 集合分组：')
    for slots, metas in sorted(slot_groups.items(), key=lambda x: min(x[1])):
        print(f'  slots={str(set(slots)):30s}  metas={sorted(metas)}')

    # 单独打印每个 metatile 的详细 slot
    print('\n--- 详细 ---')
    for mi in used_mi:
        is_pet = mi >= 512
        raw    = pet_meta_raw if is_pet else gen_meta_raw
        off    = (mi - 512 if is_pet else mi) * 16
        if off + 16 > len(raw):
            print(f'  meta[{mi}] 超出范围')
            continue
        entries = struct.unpack_from('<8H', raw, off)
        slots   = [(e >> 12) & 0xF for e in entries]
        print(f'  meta[{mi:4d}] src={"pet" if is_pet else "gen"}  '
              f'slots(8ent)={slots}')

if __name__ == '__main__':
    main()
