#!/usr/bin/env python3
"""
将 assets/tilesets/ 下每个图块集的 .pal 调色板烘焙进 tiles.png，
生成带正确颜色的 tiles_rgba.png（Godot 可直接导入的 RGBA 格式）。

用法：
    python3 tools/bake_tileset_palettes.py
"""

from pathlib import Path
from PIL import Image
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("缺少依赖：pip install Pillow")

GAME_ROOT    = Path(__file__).parent.parent
TILESETS_DIR = GAME_ROOT / "assets" / "tilesets"
SCALE        = 2   # 8px → 16px，与 TileMapZone.TILE 一致


def parse_jasc_pal(path: Path) -> list[tuple[int, int, int]]:
    colors = []
    with open(path, "r", errors="replace") as f:
        lines = [l.strip() for l in f.readlines()]
    for line in lines[3:]:
        parts = line.split()
        if len(parts) == 3:
            try:
                colors.append((int(parts[0]), int(parts[1]), int(parts[2])))
            except ValueError:
                pass
    return colors


def build_palette_bytes(pal_dir: Path) -> bytes:
    full: list[tuple[int, int, int]] = []
    for i in range(16):
        path = pal_dir / f"{i:02d}.pal"
        if path.exists():
            colors = parse_jasc_pal(path)
            full.extend(colors[:16])
        else:
            full.extend([(0, 0, 0)] * 16)
    full = full[:256]
    buf = []
    for r, g, b in full:
        buf.extend([r, g, b])
    while len(buf) < 768:
        buf.extend([0, 0, 0])
    return bytes(buf)


def bake(tileset_dir: Path) -> bool:
    tiles_path = tileset_dir / "tiles.png"
    pal_dir    = tileset_dir / "palettes"
    out_path   = tileset_dir / "tiles_rgba.png"

    if not tiles_path.exists():
        print(f"  [跳过] 无 tiles.png: {tileset_dir.name}")
        return False

    img = Image.open(tiles_path)

    if img.mode == "P":
        if pal_dir.exists():
            img.putpalette(build_palette_bytes(pal_dir))
        rgba = img.convert("RGBA")
    elif img.mode in ("RGB", "RGBA"):
        rgba = img.convert("RGBA")
    else:
        rgba = img.convert("RGBA")

    # 2× 放大：8px 原始 → 16px，与 TileMapZone.TILE 对齐
    w, h = rgba.width * SCALE, rgba.height * SCALE
    scaled = rgba.resize((w, h), Image.NEAREST)

    scaled.save(out_path)
    print(f"  [OK] {tileset_dir.name}/tiles_rgba.png  ({rgba.width}×{rgba.height} → {w}×{h}px)")
    return True


def main():
    dirs = sorted(d for d in TILESETS_DIR.iterdir() if d.is_dir() and not d.name.startswith("_"))
    if not dirs:
        sys.exit(f"未找到图块集目录: {TILESETS_DIR}")

    print(f"烘焙 {len(dirs)} 个图块集调色板...\n")
    ok = sum(1 for d in dirs if bake(d))
    print(f"\n完成：{ok}/{len(dirs)} 个 tiles_rgba.png 已生成")
    print("Godot 中请使用 tiles_rgba.png 替代 tiles.png")


if __name__ == "__main__":
    main()
