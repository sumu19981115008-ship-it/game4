#!/usr/bin/env python3
"""
从 pokeemerald 源码下载 PokemonCenter_Exterior（或 LittlerootTown）的 map.bin，
逐行打印实际使用的 metatile 网格，方便确认正确布局。
"""
import urllib.request, struct
from pathlib import Path

BASE_URL = 'https://raw.githubusercontent.com/pret/pokeemerald/master'
CACHE_DIR = Path(__file__).parent

MAPS = {
    # 可能的宝可梦中心外观地图路径（pokeemerald 中宝可梦中心外立面嵌在各城镇地图里）
    'LittlerootTown':        ('data/layouts/LittlerootTown/map.bin',        20, 20),
    'OldaleTown':            ('data/layouts/OldaleTown/map.bin',            20, 20),
    'PetalburgCity':         ('data/layouts/PetalburgCity/map.bin',         30, 20),
}

def dl(url):
    return urllib.request.urlopen(url, timeout=15).read()

for name,(path,W,H) in MAPS.items():
    cache = CACHE_DIR / f'_map_{name}.bin'
    if cache.exists():
        data = cache.read_bytes()
        print(f'缓存：{name}')
    else:
        try:
            data = dl(f'{BASE_URL}/{path}')
            cache.write_bytes(data)
            print(f'下载：{name}')
        except Exception as e:
            print(f'跳过 {name}: {e}'); continue

    cells = struct.unpack_from(f'<{W*H}H', data)
    metas = [c & 0x3FF for c in cells]
    print(f'  {name} 使用的 metatile（{W}×{H}）：')
    for r in range(H):
        row = metas[r*W:(r+1)*W]
        print('  ', row)
    # 找宝可梦中心相关图块范围（根据 custom_hub 里用的是 8-91）
    pc_metas = sorted({m for m in metas if 8<=m<=91})
    print(f'  → 宝可梦中心范围(8-91)内使用的：{pc_metas}')
    print()
